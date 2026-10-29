"""Unify existing Shadow observations, News First review queue and signed signals.

Research-only. External payloads are untrusted; this module never imports a broker
executor and never upgrades a decision to tradable/Paper eligibility.
"""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from .signal_copy import validate
except ImportError:
    from signal_copy import validate


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError('INVALID_TIMESTAMP')
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('INVALID_TIMESTAMP') from exc
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError('UNZONED_TIMESTAMP')
    return stamp.astimezone(timezone.utc)


def _identity(kind, source, value):
    digest = hashlib.sha256(json.dumps([kind, source, value], sort_keys=True, default=str).encode()).hexdigest()
    return digest[:24]


def _observation(key, value):
    if not isinstance(value, dict) or not isinstance(key, str) or ':' not in key:
        raise ValueError('INVALID_OBSERVATION')
    market, symbol = key.split(':', 1)
    if market not in ('US_EQUITY', 'B3_EQUITY', 'CRYPTO') or not symbol or value.get('market') != market or value.get('symbol') != symbol:
        raise ValueError('OBSERVATION_MISMATCH')
    if value.get('tradable_signal') is not False or value.get('paper_approved') is not False or value.get('orders_sent') != 0:
        raise ValueError('UNSAFE_OBSERVATION')
    return {'id': _identity('market', key, value.get('source_sha256')), 'kind': 'MARKET_SHADOW',
            'market': market, 'symbol': symbol, 'source': value.get('market_data_source'),
            'candidate': value.get('radar_candidate') is True, 'blockers': list(value.get('issues') or [])}


def _news(signal):
    if not isinstance(signal, dict) or not isinstance(signal.get('symbol'), str) or not signal['symbol']:
        raise ValueError('INVALID_NEWS_SIGNAL')
    if signal.get('decision') != 'NO_TRADE' or signal.get('research_status') != 'EVIDENCE_PENDING' or signal.get('quantity') != 0:
        raise ValueError('UNSAFE_NEWS_SIGNAL')
    return {'id': _identity('news', signal.get('article_id'), signal['symbol']), 'kind': 'NEWS_REVIEW',
            'market': 'UNCONFIRMED', 'symbol': signal['symbol'], 'source': signal.get('source_url'),
            'candidate': False, 'blockers': list(signal.get('blocker_reasons') or [])}


def _external(signal, secret, fx, now):
    # Signature + expiry + schema + instrument check uses existing vetted adapter.
    errors = validate(signal, secret, fx, now=now)
    return {'id': _identity('external', signal.get('provider') if isinstance(signal, dict) else None,
                            signal.get('signal_id') if isinstance(signal, dict) else None),
            'kind': 'EXTERNAL_SIGNAL', 'market': 'US_EQUITY',
            'symbol': signal.get('symbol') if isinstance(signal, dict) else None,
            'source': signal.get('provider') if isinstance(signal, dict) else None,
            'candidate': not bool(errors), 'blockers': errors + ['BROKER_PRICE_AND_PORTFOLIO_NOT_RECONCILED']}


def consolidate(observations, news=None, signals=None, *, secret='', fx=None, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('UNZONED_CLOCK')
    if not isinstance(observations, dict) or observations.get('automatic_order_submission') is not False or observations.get('usable_for_live_trading') is not False:
        raise ValueError('UNSAFE_MARKET_REPORT')
    if not isinstance(observations.get('observations'), dict):
        raise ValueError('INVALID_MARKET_REPORT')
    if news is not None and (not isinstance(news, dict) or news.get('mode') != 'NEWS_FIRST_INTERNAL_SIMULATION' or news.get('authorized_to_trade') is not False or news.get('orders_sent') != 0 or not isinstance(news.get('signals'), list)):
        raise ValueError('UNSAFE_NEWS_REPORT')
    if signals is not None and not isinstance(signals, list):
        raise ValueError('INVALID_EXTERNAL_SIGNALS')
    decisions, errors, seen = [], dict(observations.get('errors') or {}), set()
    def append(ref, maker, data):
        try:
            item = maker(data)
            if item['id'] in seen:
                errors[ref] = 'DUPLICATE_SIGNAL'
                return
            seen.add(item['id'])
            item.update({'decision': 'RESEARCH_ONLY', 'paper_approved': False,
                         'tradable_signal': False, 'orders_sent': 0})
            decisions.append(item)
        except (ValueError, TypeError, KeyError) as exc:
            errors[ref] = f'{type(exc).__name__}: {exc}'
    for key, value in sorted(observations['observations'].items()):
        append('market:' + str(key), lambda x, key=key: _observation(key, x), value)
    if news:
        for idx, value in enumerate(news['signals']):
            append('news:' + str(idx), _news, value)
    for idx, value in enumerate(signals or []):
        append('external:' + str(idx), lambda x: _external(x, secret, fx, now), value)
    return {'schema_version': 'v4-signal-intelligence-1', 'generated_at_utc': now.isoformat(),
            'status': 'RESEARCH_ONLY' if not errors else 'PARTIAL_OR_BLOCKED',
            'decisions': decisions, 'errors': errors, 'paper_approved': False,
            'automatic_order_submission': False, 'usable_for_live_trading': False, 'orders_sent': 0}


def main():
    parser = argparse.ArgumentParser(description='Offline, fail-closed multi-source decision report')
    parser.add_argument('--observations', required=True)
    parser.add_argument('--news', help='News First simulation-signals JSON, not raw articles')
    parser.add_argument('--signed-signals', help='JSON array of signed external signals; avoid raw webhook tokens')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        print(json.dumps({'status': 'BLOCKED_LIVE_FLAG', 'orders_sent': 0})); return 2
    try:
        observations = json.loads(Path(args.observations).read_text(encoding='utf-8'))
        news = json.loads(Path(args.news).read_text(encoding='utf-8')) if args.news else None
        signals = json.loads(Path(args.signed_signals).read_text(encoding='utf-8')) if args.signed_signals else None
        fx = os.getenv('USD_BRL_REFERENCE')
        # Existing adapter uses USD/BRL reference; missing FX fails the external preview closed.
        from decimal import Decimal
        fx = Decimal(fx) if fx else None
        result = consolidate(observations, news, signals, secret=os.getenv('SIGNAL_COPY_SECRET', ''), fx=fx)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.is_symlink(): raise ValueError('SYMLINK_OUTPUT_FORBIDDEN')
        tmp = output.with_suffix(output.suffix + '.tmp')
        tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        tmp.replace(output)
        print(json.dumps({'status': result['status'], 'decisions': len(result['decisions']),
                          'errors': result['errors'], 'orders_sent': 0, 'output': str(output)}))
        return 0 if not result['errors'] else 2
    except (ValueError, TypeError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
