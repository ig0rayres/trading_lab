"""Read-only FIFO P&L from individually identified broker fill activities.

This is an independently calculated estimate, never broker-verified P&L. Activity
provenance/completeness, financing, corporate actions and fees must be verified
externally before reporting an authoritative realized result.
"""
import argparse
import json
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path


def positive(value, label, allow_zero=False):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('INVALID_' + label)
    if not result.is_finite() or (result < 0 if allow_zero else result <= 0):
        raise ValueError('INVALID_' + label)
    return result


def calculate(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('activities'), list):
        raise ValueError('INVALID_ACTIVITIES')
    if payload.get('complete') is not True:
        raise ValueError('INCOMPLETE_ACTIVITY_HISTORY')
    currency = payload.get('currency')
    if currency not in ('USD', 'BRL'):
        raise ValueError('UNSUPPORTED_CURRENCY')
    seen, holdings, events = set(), {}, []
    realized = Decimal('0')
    for item in payload['activities']:
        if not isinstance(item, dict):
            raise ValueError('INVALID_ACTIVITY')
        ident = item.get('id')
        symbol = item.get('symbol')
        side = item.get('side')
        timestamp = item.get('timestamp')
        if not isinstance(ident, str) or not ident or ident in seen:
            raise ValueError('DUPLICATE_OR_INVALID_ACTIVITY_ID')
        if not isinstance(symbol, str) or not symbol or symbol != symbol.upper() or side not in ('buy', 'sell'):
            raise ValueError('INVALID_ACTIVITY_IDENTITY')
        if not isinstance(timestamp, str) or not timestamp:
            raise ValueError('MISSING_ACTIVITY_TIMESTAMP')
        seen.add(ident)
        quantity = positive(item.get('qty'), 'QTY')
        price = positive(item.get('price'), 'PRICE')
        if 'fee' not in item:
            raise ValueError('UNKNOWN_FEES')
        fee = positive(item['fee'], 'FEE', allow_zero=True)
        lots = holdings.setdefault(symbol, [])
        if side == 'buy':
            lots.append([quantity, price + fee / quantity])
            events.append({'id': ident, 'symbol': symbol, 'type': 'open_or_add', 'qty': str(quantity)})
            continue
        available = sum((lot[0] for lot in lots), Decimal('0'))
        if quantity > available:
            raise ValueError('SHORT_OR_MISSING_BUY_HISTORY')
        remain, cost = quantity, Decimal('0')
        while remain:
            lotqty, unitcost = lots[0]
            take = min(remain, lotqty)
            cost += take * unitcost
            remain -= take
            if take == lotqty:
                lots.pop(0)
            else:
                lots[0][0] -= take
        pnl = quantity * price - fee - cost
        realized += pnl
        events.append({'id': ident, 'symbol': symbol, 'type': 'partial_or_full_close',
                       'qty': str(quantity), 'realized_pnl': str(pnl), 'currency': currency})
    return {'schema_version': 'v4-activity-fifo-ledger-1', 'mode': 'READ_ONLY',
            'source': 'SUPPLIED_ACTIVITY_HISTORY', 'currency': currency,
            'realized_pnl_calculated': str(realized), 'realized_pnl_verified': False,
            'broker_reconciled': False, 'fees_supplied_not_verified': True,
            'open_positions': {k: str(sum((lot[0] for lot in v), Decimal('0'))) for k, v in holdings.items() if v},
            'events': events, 'execution_authorized': False, 'orders_sent': 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only FIFO ledger from supplied broker fill activities')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        print(json.dumps({'status': 'BLOCKED_LIVE_FLAG', 'orders_sent': 0})); return 2
    try:
        output = Path(args.output)
        if output.suffix != '.json' or output.is_symlink() or output.resolve() == Path(args.input).resolve():
            raise ValueError('UNSAFE_OUTPUT')
        report = calculate(json.loads(Path(args.input).read_text(encoding='utf-8')))
        output.parent.mkdir(parents=True, exist_ok=True)
        temp = output.with_suffix('.json.tmp')
        if temp.is_symlink():
            raise ValueError('UNSAFE_TEMP')
        with temp.open('w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            f.flush(); os.fsync(f.fileno())
        os.replace(temp, output)
        print(json.dumps({'status': 'READ_ONLY', 'events': len(report['events']), 'orders_sent': 0})); return 0
    except (ValueError, OSError, TypeError, KeyError, ArithmeticError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc), 'orders_sent': 0})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
