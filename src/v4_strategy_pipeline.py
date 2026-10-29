"""Fail-closed conversion of public research candles into Shadow candidates.

Vendor payloads are never evidence of issuer quality or reviewed catalysts.
Outputs are research observations, NOT executable trading signals.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from .market_opportunities import inspect
except ImportError:
    from market_opportunities import inspect

MARKETS = {'US_EQUITY', 'B3_EQUITY', 'CRYPTO'}


def assess_feed(feed, *, now=None):
    if not isinstance(feed, dict) or feed.get('market') not in MARKETS:
        raise ValueError('INVALID_MARKET_FEED')
    if (feed.get('usable_for_live_trading') is not False or
            feed.get('independent_market_verification') is not False or
            feed.get('provenance_level') not in ('SINGLE_PUBLIC_DATA_PROVIDER', 'SINGLE_PUBLIC_EXCHANGE_RESPONSE')):
        raise ValueError('UNTRUSTED_FEED_FLAGS')
    market, symbol = feed['market'], feed.get('symbol')
    if not isinstance(symbol, str) or not symbol:
        raise ValueError('INVALID_SYMBOL')
    denomination = 'USD' if market == 'US_EQUITY' else 'BRL'
    if feed.get('denomination') != denomination:
        raise ValueError('DENOMINATION_MISMATCH')
    bars = feed.get('bars')
    if not isinstance(bars, list) or len(bars) < 6 or len(bars) > 2000:
        raise ValueError('INSUFFICIENT_OR_EXCESS_BARS')
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('UNZONED_CLOCK')
    converted = []
    for bar in bars:
        if not isinstance(bar, dict) or bar.get('complete') is not True or bar.get('verified') is not False:
            raise ValueError('UNTRUSTED_OR_INCOMPLETE_BAR')
        timestamp = bar.get('at_utc')
        if not isinstance(timestamp, str):
            raise ValueError('INVALID_BAR_TIME')
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        if dt.tzinfo is None or dt.utcoffset() is None or dt > now:
            raise ValueError('UNZONED_OR_FUTURE_BAR')
        suffix = '_brl' if market == 'CRYPTO' else ''
        # Neither public collector provides trustworthy volume yet. Zero denotes
        # unavailable volume, never an observed market volume of zero.
        converted.append({'at': dt.astimezone(timezone.utc).isoformat(),
                          'close': bar['close' + suffix], 'high': bar['high' + suffix],
                          'low': bar['low' + suffix], 'volume': 0})
    observation = inspect({'market': market, 'symbol': symbol, 'bars': converted,
                           'quality_verified': False, 'event_reviewed': False})
    observation.update({'market_data_source': feed.get('venue'),
                        'source_sha256': feed.get('source_sha256'),
                        'denomination': denomination,
                        'volume_available': False,
                        'source_independently_verified': False,
                        'tradable_signal': False, 'paper_approved': False,
                        'orders_sent': 0})
    return observation


def run(cycle, *, now=None):
    if not isinstance(cycle, dict) or cycle.get('automatic_order_submission') is not False or cycle.get('usable_for_live_trading') is not False:
        raise ValueError('UNSAFE_CYCLE')
    results, errors = {}, dict(cycle.get('errors') or {})
    if not isinstance(cycle.get('results'), dict):
        raise ValueError('INVALID_RESULTS')
    for key, feed in cycle['results'].items():
        try:
            if not isinstance(key, str) or key != f"{feed['market']}:{feed['symbol']}":
                raise ValueError('FEED_KEY_MISMATCH')
            results[key] = assess_feed(feed, now=now)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            errors[str(key)] = f'{type(exc).__name__}: {exc}'
    return {'schema_version': 'v4-strategy-observations-1',
            'status': 'RESEARCH_ONLY' if not errors else 'PARTIAL_OR_BLOCKED',
            'generated_at_utc': (now or datetime.now(timezone.utc)).isoformat(),
            'observations': results, 'errors': errors,
            'automatic_order_submission': False, 'usable_for_live_trading': False}


def main():
    parser = argparse.ArgumentParser(description='Offline Shadow scoring from market-cycle JSON')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    cycle = json.loads(Path(args.input).read_text(encoding='utf-8'))
    result = run(cycle)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'observations': len(result['observations']),
                      'errors': result['errors'], 'output': str(dest)}))
    return 2 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
