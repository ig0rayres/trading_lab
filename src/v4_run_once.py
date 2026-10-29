"""One-shot, fail-closed orchestration of market research, signals and risk preview.

This process intentionally cannot place broker orders. Each stage is persisted
atomically with an explicit status and the run exits nonzero on partial data.
"""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from .v4_market_cycle import collect
    from .v4_decision_cycle import run as decide
    from .v4_decision_risk import assess
except ImportError:
    from v4_market_cycle import collect
    from v4_decision_cycle import run as decide
    from v4_decision_risk import assess

MARKETS = {'US_EQUITY', 'B3_EQUITY', 'CRYPTO'}


def parse_universe(data):
    if not isinstance(data, list) or not 1 <= len(data) <= 250:
        raise ValueError('INVALID_UNIVERSE_SIZE')
    result, seen = [], set()
    for item in data:
        if not isinstance(item, dict) or set(item) != {'market', 'symbol'}:
            raise ValueError('INVALID_UNIVERSE_ITEM')
        market, symbol = item['market'], item['symbol']
        if not isinstance(market, str) or market not in MARKETS or not isinstance(symbol, str):
            raise ValueError('INVALID_INSTRUMENT')
        if not 1 <= len(symbol) <= 20 or not symbol.isascii() or not symbol.isalnum() or symbol != symbol.upper():
            raise ValueError('INVALID_SYMBOL')
        key = (market, symbol)
        if key in seen:
            raise ValueError('DUPLICATE_SYMBOL')
        seen.add(key)
        result.append(key)
    return result


def build(universe, *, equity_fetch=None, crypto_fetch=None, news=None, signals=None, secret='', fx=None, portfolio=None, tickets=None, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('INVALID_CLOCK')
    market = collect(universe, equity_fetch=equity_fetch, crypto_fetch=crypto_fetch)
    decisions = decide(market, news, signals, secret=secret, fx=fx, now=now)
    risk = assess(decisions, portfolio, tickets)
    partial = bool(market['errors'] or decisions['errors'] or risk['status'] != 'RESEARCH_ONLY')
    manifest = {'schema_version': 'v4-once-1', 'timestamp_utc': now.isoformat(),
                'status': 'PARTIAL_OR_BLOCKED' if partial else 'RESEARCH_ONLY',
                'market_count': len(market['results']), 'decision_count': len(decisions['decisions']),
                'risk_count': len(risk['results']), 'execution_authorized': False,
                'automatic_order_submission': False, 'orders_sent': 0,
                'limitations': ['RESEARCH_FEEDS_UNVERIFIED', 'GLOBAL_BROKER_PORTFOLIO_NOT_ATTESTED',
                                'PAPER_EXECUTION_NOT_HOMOLOGATED']}
    return {'manifest': manifest, 'market': market, 'decisions': decisions, 'risk': risk}


def atomic_json(path, data):
    path = Path(path)
    if path.is_symlink() or path.suffix != '.json':
        raise ValueError('UNSAFE_REPORT_PATH')
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.json.tmp')
    if tmp.is_symlink():
        raise ValueError('UNSAFE_TEMP_PATH')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main(argv=None):
    p = argparse.ArgumentParser(description='Read-only, one-shot three-market research pipeline')
    p.add_argument('--universe', required=True, help='JSON array of {market,symbol} objects')
    p.add_argument('--output-dir', required=True)
    p.add_argument('--news')
    p.add_argument('--signals')
    args = p.parse_args(argv)
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        print(json.dumps({'status': 'BLOCKED_LIVE_FLAG', 'orders_sent': 0}))
        return 2
    try:
        universe = parse_universe(json.loads(Path(args.universe).read_text(encoding='utf-8')))
        news = json.loads(Path(args.news).read_text(encoding='utf-8')) if args.news else None
        signals = json.loads(Path(args.signals).read_text(encoding='utf-8')) if args.signals else None
        from decimal import Decimal
        fx = os.getenv('USD_BRL_REFERENCE')
        result = build(universe, news=news, signals=signals, secret=os.getenv('SIGNAL_COPY_SECRET', ''), fx=Decimal(fx) if fx else None)
        folder = Path(args.output_dir)
        if folder.is_symlink():
            raise ValueError('UNSAFE_OUTPUT_DIRECTORY')
        # Publish the manifest last. It binds the three component reports by hash,
        # so a crashed/overlapping write cannot appear as a complete new cycle.
        components = ('market', 'decisions', 'risk')
        for name in components:
            atomic_json(folder / ('v4_' + name + '.json'), result[name])
        result['manifest']['component_sha256'] = {
            name: hashlib.sha256((folder / ('v4_' + name + '.json')).read_bytes()).hexdigest()
            for name in components
        }
        atomic_json(folder / 'v4_manifest.json', result['manifest'])
        print(json.dumps({'status': result['manifest']['status'], 'decisions': result['manifest']['decision_count'], 'orders_sent': 0}))
        return 0 if result['manifest']['status'] == 'RESEARCH_ONLY' else 2
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc)[:150], 'orders_sent': 0}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
