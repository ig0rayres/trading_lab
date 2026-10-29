"""One-shot, fail-closed Alpaca Paper evidence bundle. Never authorizes orders.

Checks consistency of observed fill quantities against broker positions, but does
not infer full history, fee completeness, cash or globally reconciled risk.
"""
import argparse
import json
import os
from pathlib import Path

try:
    from .v4_alpaca_activities import fetch_pages
    from .v4_broker_snapshot import collect
    from .v4_fill_position_check import compare
    from .v4_run_once import atomic_json
    from .paper_audit import get_json
except ImportError:
    from v4_alpaca_activities import fetch_pages
    from v4_broker_snapshot import collect
    from v4_fill_position_check import compare
    from v4_run_once import atomic_json
    from paper_audit import get_json


def reconcile(env, *, fetch_activities=fetch_pages, fetch_snapshot=collect,
              fetch_positions=None, raw_positions=None):
    if env.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        raise ValueError('LIVE_TRADING_FORBIDDEN')
    activities = fetch_activities(env)
    snapshot = fetch_snapshot(env)
    if raw_positions is None and fetch_positions is not None:
        raw_positions = fetch_positions(env)
    if raw_positions is None:
        # Snapshot normalizes notional but not quantities. The raw broker positions
        # must be supplied separately; never claim a quantity match without them.
        return {'schema_version': 'v4-alpaca-reconciliation-1', 'mode': 'READ_ONLY',
                'status': 'BLOCKED_INCOMPLETE', 'activities': activities,
                'snapshot': snapshot, 'quantity_check': None,
                'blocking_reasons': ['RAW_POSITIONS_NOT_SUPPLIED', 'COMPLETE_HISTORY_UNVERIFIED',
                                     'CROSS_MARKET_RISK_UNVERIFIED'],
                'broker_reconciled': False, 'execution_authorized': False, 'orders_sent': 0}
    check = compare(activities, raw_positions)
    return {'schema_version': 'v4-alpaca-reconciliation-1', 'mode': 'READ_ONLY',
            'status': 'BLOCKED_INCOMPLETE', 'activities': activities,
            'snapshot': snapshot, 'quantity_check': check,
            'blocking_reasons': list(dict.fromkeys(check['blocking_reasons'] +
                ['CROSS_MARKET_RISK_UNVERIFIED', 'BROKER_CASH_NOT_RECONCILED'])),
            'broker_reconciled': False, 'execution_authorized': False, 'orders_sent': 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only, incomplete Alpaca Paper evidence bundle')
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        out = Path(args.output)
        if out.suffix != '.json' or out.is_symlink():
            raise ValueError('UNSAFE_OUTPUT')
        report = reconcile(os.environ, fetch_positions=lambda env: get_json('/v2/positions', env))
        atomic_json(out, report)
        print(json.dumps({'status': report['status'], 'orders_sent': 0}))
        return 2
    except (ValueError, TypeError, OSError, KeyError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
