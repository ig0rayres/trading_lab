"""Conservative read-only order lifecycle reconciliation from Alpaca GET snapshots.

A broker-reported fill is not a closed trade, realized P&L, or evidence that
stops remain protected. This module never authorizes/sends orders.
"""
import argparse
import json
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

TERMINAL = {'filled', 'canceled', 'expired', 'rejected', 'done_for_day'}
VALID = TERMINAL | {'new', 'accepted', 'pending_new', 'accepted_for_bidding', 'partially_filled',
                    'pending_cancel', 'pending_replace', 'replaced', 'stopped', 'suspended', 'calculated', 'held'}


def qty(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError('INVALID_QUANTITY')
    if not result.is_finite() or result < 0:
        raise ValueError('INVALID_QUANTITY')
    return result


def normalize(order):
    if not isinstance(order, dict):
        raise ValueError('INVALID_ORDER')
    oid, status = order.get('id'), order.get('status')
    if not isinstance(oid, str) or not oid.strip() or status not in VALID:
        raise ValueError('INVALID_ORDER_ID_OR_STATUS')
    symbol, side = order.get('symbol'), order.get('side')
    if not isinstance(symbol, str) or not symbol.strip() or side not in {'buy', 'sell'}:
        raise ValueError('INVALID_SYMBOL_OR_SIDE')
    ordered, filled = qty(order.get('qty')), qty(order.get('filled_qty', '0'))
    if ordered <= 0 or filled > ordered:
        raise ValueError('INVALID_FILL_QUANTITY')
    if status == 'filled' and filled != ordered:
        raise ValueError('INCONSISTENT_FILLED_STATUS')
    if status == 'partially_filled' and not (0 < filled < ordered):
        raise ValueError('INCONSISTENT_PARTIAL_STATUS')
    price = order.get('filled_avg_price')
    if filled > 0:
        if price is None or qty(price) <= 0:
            raise ValueError('INVALID_FILL_PRICE')
    elif price not in (None, ''):
        raise ValueError('UNEXPECTED_FILL_PRICE')
    return {'broker_order_id': oid, 'client_order_id': order.get('client_order_id'),
            'symbol': symbol.strip().upper(), 'side': side, 'status': status,
            'ordered_qty': str(ordered), 'filled_qty': str(filled),
            'filled_avg_price': str(qty(price)) if filled else None,
            'filled_at': order.get('filled_at'), 'terminal': status in TERMINAL}


def reconcile_snapshot(payload):
    """Observe order graph. Never infer completeness from missing orders/legs."""
    if not isinstance(payload, dict) or not isinstance(payload.get('orders'), list):
        raise ValueError('INVALID_SNAPSHOT')
    seen = set()
    events = []
    issues = []
    for order in payload['orders']:
        root = normalize(order)
        if root['broker_order_id'] in seen:
            raise ValueError('DUPLICATE_BROKER_ORDER')
        seen.add(root['broker_order_id'])
        events.append(root)
        legs = order.get('legs')
        if order.get('order_class') in ('bracket', 'oto', 'oco') and not isinstance(legs, list):
            issues.append('MISSING_BRACKET_LEGS:' + root['broker_order_id'])
        if legs is not None:
            if not isinstance(legs, list):
                raise ValueError('INVALID_ORDER_LEGS')
            for leg in legs:
                child = normalize(leg)
                if child['broker_order_id'] in seen:
                    raise ValueError('DUPLICATE_BROKER_ORDER')
                if child['symbol'] != root['symbol']:
                    raise ValueError('MISMATCHED_LEG_SYMBOL')
                seen.add(child['broker_order_id'])
                events.append(child)
    return {'schema_version': 'v4-paper-order-observation-1', 'source': 'ALPACA_PAPER_GET_ONLY',
            'mode': 'READ_ONLY', 'orders': events, 'issues': issues,
            'has_partial_fills': any(e['status'] == 'partially_filled' for e in events),
            'observed_fill_count': sum(Decimal(e['filled_qty']) > 0 for e in events),
            'broker_reconciled': False, 'pnl_verified': False,
            'realized_pnl_brl': None, 'positions_closed_verified': False,
            'execution_authorized': False, 'orders_sent': 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only broker order observation, no submission')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        print(json.dumps({'status': 'BLOCKED_LIVE_FLAG', 'orders_sent': 0})); return 2
    try:
        output = Path(args.output)
        if output.suffix != '.json' or output.is_symlink():
            raise ValueError('UNSAFE_OUTPUT')
        observed = reconcile_snapshot(json.loads(Path(args.input).read_text(encoding='utf-8')))
        output.parent.mkdir(parents=True, exist_ok=True)
        temp = output.with_suffix('.json.tmp')
        if temp.is_symlink():
            raise ValueError('UNSAFE_TEMP')
        temp.write_text(json.dumps(observed, indent=2) + '\n', encoding='utf-8')
        temp.replace(output)
        print(json.dumps({'status': 'READ_ONLY', 'orders_observed': len(observed['orders']), 'orders_sent': 0}))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
