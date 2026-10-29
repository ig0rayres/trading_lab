"""Single fail-closed research cycle: market data -> scanner -> multi-source decisions.

This process deliberately does not import or invoke order submission code.
"""
import argparse
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

try:
    from .v4_strategy_pipeline import run as scan
    from .v4_signal_intelligence import consolidate
except ImportError:
    from v4_strategy_pipeline import run as scan
    from v4_signal_intelligence import consolidate


def run(cycle, news=None, signals=None, *, secret='', fx=None, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError('UNZONED_CLOCK')
    observation = scan(cycle, now=now)
    decision = consolidate(observation, news, signals, secret=secret, fx=fx, now=now)
    # A partial upstream market scan cannot be represented as a clean decision run.
    if observation['errors']:
        decision['status'] = 'PARTIAL_OR_BLOCKED'
    decision['market_cycle_errors'] = dict(observation['errors'])
    decision['scanned_markets'] = len(observation['observations'])
    decision['pipeline'] = 'market_cycle -> shadow_scanner -> signal_intelligence'
    return decision


def _read(path):
    if not path:
        return None
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline, read-only v4 decision pipeline')
    parser.add_argument('--market-cycle', required=True)
    parser.add_argument('--news')
    parser.add_argument('--signed-signals')
    parser.add_argument('--output', required=True)
    parser.add_argument('--risk-output', help='Optional read-only risk preview JSON')
    parser.add_argument('--risk-snapshot', help='Optional external reconciled portfolio snapshot')
    parser.add_argument('--risk-tickets', help='Optional proposed tickets keyed by decision id')
    args = parser.parse_args(argv)
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        print(json.dumps({'status': 'BLOCKED_LIVE_FLAG', 'orders_sent': 0}))
        return 2
    try:
        fx_s = os.getenv('USD_BRL_REFERENCE')
        fx = Decimal(fx_s) if fx_s else None
        output = Path(args.output)
        if output.is_symlink() or output.suffix.lower() != '.json':
            raise ValueError('UNSAFE_OUTPUT')
        result = run(_read(args.market_cycle), _read(args.news), _read(args.signed_signals),
                     secret=os.getenv('SIGNAL_COPY_SECRET', ''), fx=fx)
        if args.risk_output:
            try:
                from .v4_decision_risk import assess
            except ImportError:
                from v4_decision_risk import assess
            risk_path = Path(args.risk_output)
            if risk_path == output or risk_path.suffix.lower() != '.json' or risk_path.is_symlink():
                raise ValueError('UNSAFE_RISK_OUTPUT')
            snapshot = _read(args.risk_snapshot)
            tickets = _read(args.risk_tickets)
            risk_preview = assess(result, snapshot, tickets)
            risk_path.parent.mkdir(parents=True, exist_ok=True)
            risk_tmp = risk_path.with_suffix('.json.tmp')
            if risk_tmp.is_symlink():
                raise ValueError('UNSAFE_RISK_TEMP')
            risk_tmp.write_text(json.dumps(risk_preview, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            risk_tmp.replace(risk_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        tmp = output.with_suffix('.json.tmp')
        if tmp.is_symlink():
            raise ValueError('UNSAFE_TEMP_OUTPUT')
        tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        tmp.replace(output)
        print(json.dumps({'status': result['status'], 'decisions': len(result['decisions']),
                          'errors': result['errors'], 'market_errors': result['market_cycle_errors'],
                          'orders_sent': 0, 'output': str(output)}))
        return 0 if result['status'] == 'RESEARCH_ONLY' else 2
    except (ValueError, TypeError, KeyError, OSError, InvalidOperation, OverflowError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
