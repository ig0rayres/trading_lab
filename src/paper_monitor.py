"""One-shot, read-only Paper order monitor. No automatic submission or broker mutations."""
import argparse
import fcntl
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from paper_reconcile import reconcile

DEFAULT_LOG = Path('/app/reports/paper/order-snapshots.jsonl')


def analyze(order):
    if order.get('status') != 'RECONCILED':
        return {'status': order.get('status'), 'orders_sent': 0}
    entry_qty = Decimal(str(order.get('filled_qty') or '0'))
    entry_price = Decimal(str(order.get('filled_avg_price') or '0'))
    legs = order.get('legs', [])
    exits = [leg for leg in legs if Decimal(str(leg.get('filled_qty') or '0')) > 0]
    closed_qty = sum((Decimal(str(x['filled_qty'])) for x in exits), Decimal('0'))
    pnl = sum((Decimal(str(x['filled_qty'])) *
               (Decimal(str(x.get('filled_avg_price') or '0')) - entry_price) for x in exits), Decimal('0'))
    if closed_qty > entry_qty:
        return {'status': 'INCONSISTENT_BROKER_QUANTITIES', 'orders_sent': 0}
    bracket_types = {x.get('type') for x in legs}
    return {'status': 'MONITORED', 'client_order_id': order['client_order_id'],
            'broker_order_id': order.get('broker_order_id'), 'symbol': order.get('symbol'),
            'entry_status': order.get('broker_status'), 'entry_qty': str(entry_qty),
            'entry_price': str(entry_price), 'closed_qty': str(closed_qty),
            'remaining_qty': str(entry_qty - closed_qty),
            'realized_gross_pnl_usd': str(pnl),
            'pnl_is_net': False, 'exit_legs': legs,
            'bracket_legs_observed': bool({'limit', 'stop'} <= bracket_types),
            'orders_sent': 0}


def record(snapshot, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {'at': datetime.now(timezone.utc).isoformat(), **snapshot}
    with path.open('a', encoding='utf-8') as fp:
        fcntl.flock(fp, fcntl.LOCK_EX)
        fp.write(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n')
        fp.flush()
        os.fsync(fp.fileno())
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client-order-id', required=True)
    parser.add_argument('--output', default=str(DEFAULT_LOG))
    args = parser.parse_args()
    result = analyze(reconcile(args.client_order_id, os.environ))
    if result['status'] == 'MONITORED':
        record(result, Path(args.output))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['status'] == 'MONITORED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
