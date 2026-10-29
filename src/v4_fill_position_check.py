"""Conservative read-only consistency check of Alpaca fill history versus positions.

A position match is not a fee/P&L reconciliation. Incomplete activity history,
corporate actions, transfers, fractional adjustments and fees remain blockers.
"""
import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def decimal(value, name, *, zero=True):
    try:
        number = Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        raise ValueError('INVALID_' + name)
    if not number.is_finite() or number < 0 or (not zero and number == 0):
        raise ValueError('INVALID_' + name)
    return number


def compare(activities, positions):
    if not isinstance(activities, dict) or activities.get('source') != 'ALPACA_PAPER_ACTIVITIES_GET':
        raise ValueError('UNTRUSTED_ACTIVITY_SOURCE')
    if not isinstance(activities.get('activities'), list):
        raise ValueError('INVALID_ACTIVITIES')
    if not isinstance(positions, list):
        raise ValueError('INVALID_POSITIONS')
    totals, seen = {}, set()
    for event in activities['activities']:
        if not isinstance(event, dict) or not isinstance(event.get('id'), str) or not event['id'] or event['id'] in seen:
            raise ValueError('INVALID_OR_DUPLICATE_ACTIVITY')
        seen.add(event['id'])
        symbol, side = event.get('symbol'), event.get('side')
        if not isinstance(symbol, str) or not symbol or symbol.upper() != symbol or side not in ('buy', 'sell'):
            raise ValueError('INVALID_ACTIVITY_IDENTITY')
        qty = decimal(event.get('qty'), 'ACTIVITY_QTY', zero=False)
        totals[symbol] = totals.get(symbol, Decimal(0)) + (qty if side == 'buy' else -qty)
    broker, observed = {}, set()
    for position in positions:
        if not isinstance(position, dict):
            raise ValueError('INVALID_POSITION')
        symbol = position.get('symbol')
        if not isinstance(symbol, str) or not symbol or symbol.upper() != symbol or symbol in observed:
            raise ValueError('INVALID_OR_DUPLICATE_POSITION')
        observed.add(symbol)
        if position.get('side') != 'long':
            raise ValueError('SHORT_POSITION_NOT_SUPPORTED')
        broker[symbol] = decimal(position.get('qty'), 'POSITION_QTY', zero=False)
    differences = []
    for symbol in sorted(set(totals) | set(broker)):
        activity_qty = totals.get(symbol, Decimal(0))
        broker_qty = broker.get(symbol, Decimal(0))
        if activity_qty != broker_qty:
            differences.append({'symbol': symbol, 'activity_net_qty': str(activity_qty), 'broker_qty': str(broker_qty)})
    history_complete = activities.get('complete') is True and activities.get('history_boundary_verified') is True
    return {'schema_version': 'v4-fill-position-check-1', 'mode': 'READ_ONLY',
            'source': 'ALPACA_PAPER_ACTIVITIES_AND_POSITIONS',
            'position_quantities_match': not differences,
            'differences': differences, 'activity_history_complete': history_complete,
            'fees_verified': activities.get('fees_verified') is True,
            'broker_reconciled': False, 'realized_pnl_verified': False,
            'execution_authorized': False, 'orders_sent': 0,
            'blocking_reasons': ([ 'ACTIVITY_POSITION_MISMATCH' ] if differences else []) +
            ([] if history_complete else ['INCOMPLETE_ACTIVITY_HISTORY']) +
            ([] if activities.get('fees_verified') is True else ['FEES_UNVERIFIED']) +
            ['CASH_AND_CORPORATE_ACTIONS_NOT_RECONCILED']}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only comparison of Paper fills and positions')
    parser.add_argument('--activities', required=True)
    parser.add_argument('--positions', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        out = Path(args.output)
        if out.suffix != '.json' or out.is_symlink() or out.resolve() in (Path(args.activities).resolve(), Path(args.positions).resolve()):
            raise ValueError('UNSAFE_OUTPUT')
        activities = json.loads(Path(args.activities).read_text(encoding='utf-8'))
        positions_input = json.loads(Path(args.positions).read_text(encoding='utf-8'))
        positions = positions_input['positions'] if isinstance(positions_input, dict) else positions_input
        report = compare(activities, positions)
        out.parent.mkdir(parents=True, exist_ok=True)
        temp = out.with_suffix('.json.tmp')
        if temp.is_symlink():
            raise ValueError('UNSAFE_TEMP')
        temp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temp.replace(out)
        print(json.dumps({'status': 'READ_ONLY_UNRECONCILED', 'mismatches': len(report['differences']), 'orders_sent': 0}))
        return 0 if report['position_quantities_match'] else 2
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc)[:100], 'orders_sent': 0}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
