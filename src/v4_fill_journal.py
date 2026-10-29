"""Append-only observation journal for cumulative Alpaca Paper order GET snapshots.

No orders, positions, cash or realized P&L are inferred from these observations.
Source authenticity and completeness must be established outside this module.
"""
import argparse
import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path
from v4_order_lifecycle import reconcile_snapshot

SCHEMA = 'v4-fill-observation-journal-1'


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def digest(obj):
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def inspect(existing):
    if not isinstance(existing, dict) or existing.get('schema_version') != SCHEMA:
        raise ValueError('INVALID_JOURNAL')
    rows = existing.get('events')
    if not isinstance(rows, list):
        raise ValueError('INVALID_EVENTS')
    last = '0' * 64
    current = {}
    for row in rows:
        if not isinstance(row, dict) or row.get('previous_hash') != last:
            raise ValueError('BROKEN_JOURNAL_CHAIN')
        body = {k: v for k, v in row.items() if k != 'hash'}
        if digest(body) != row.get('hash'):
            raise ValueError('TAMPERED_JOURNAL')
        last = row['hash']
        oid = row.get('broker_order_id')
        if not isinstance(oid, str) or not oid:
            raise ValueError('INVALID_ORDER_ID')
        if row.get('type') not in {'observed', 'fill_increase'}:
            raise ValueError('INVALID_EVENT_TYPE')
        previous = current.get(oid)
        total = Decimal(row['cumulative_filled_qty'])
        if total < 0 or not total.is_finite():
            raise ValueError('INVALID_CUMULATIVE_FILL')
        if previous and (previous['symbol'] != row['symbol'] or previous['side'] != row['side'] or total < previous['filled']):
            raise ValueError('INCONSISTENT_JOURNAL_PROGRESS')
        if previous and row['type'] != 'fill_increase' and total > previous['filled']:
            raise ValueError('INVALID_EVENT_TYPE')
        if previous and row['type'] == 'fill_increase' and total <= previous['filled']:
            raise ValueError('INVALID_EVENT_TYPE')
        current[oid] = {'filled': total, 'symbol': row['symbol'], 'side': row['side'], 'status': row['status'], 'price': row['filled_avg_price']}
    return current, last


def update_journal(existing, snapshot):
    """Pure function: reconcile cumulative order snapshots, never double count identical fills."""
    data = reconcile_snapshot(snapshot)
    if existing is None:
        existing = {'schema_version': SCHEMA, 'events': []}
    current, previous_hash = inspect(existing)
    seen = []
    events = list(existing['events'])
    for order in data['orders']:
        oid = order['broker_order_id']
        prior = current.get(oid)
        filled = Decimal(order['filled_qty'])
        if prior and (prior['symbol'] != order['symbol'] or prior['side'] != order['side']):
            raise ValueError('ORDER_IDENTITY_CHANGED')
        if prior and filled < prior['filled']:
            raise ValueError('FILL_REGRESSION')
        if prior and filled == prior['filled']:
            if filled and prior['price'] != order['filled_avg_price']:
                raise ValueError('FILL_PRICE_CHANGED_WITHOUT_QUANTITY')
            seen.append(oid)
            continue
        event = {'type': 'fill_increase' if filled > 0 else 'observed',
                 'broker_order_id': oid, 'client_order_id': order['client_order_id'],
                 'symbol': order['symbol'], 'side': order['side'], 'status': order['status'],
                 'cumulative_filled_qty': str(filled),
                 'incremental_filled_qty': str(filled - (prior['filled'] if prior else 0)),
                 'filled_avg_price': order['filled_avg_price'], 'filled_at': order['filled_at'],
                 'previous_hash': previous_hash}
        event['hash'] = digest(event)
        previous_hash = event['hash']
        events.append(event)
        seen.append(oid)
    return {'schema_version': SCHEMA, 'events': events}, {
        'mode': 'READ_ONLY', 'source': 'UNATTESTED_ORDER_SNAPSHOT',
        'orders_in_snapshot': len(seen), 'new_events': len(events) - len(existing['events']),
        'total_events': len(events), 'snapshot_issues': data['issues'],
        'broker_reconciled': False, 'realized_pnl_verified': False,
        'realized_pnl_brl': None, 'execution_authorized': False, 'orders_sent': 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only cumulative fill observation journal')
    parser.add_argument('--input', required=True)
    parser.add_argument('--journal', required=True)
    args = parser.parse_args(argv)
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        print(json.dumps({'status': 'BLOCKED_LIVE_FLAG', 'orders_sent': 0})); return 2
    try:
        path = Path(args.journal)
        if path.suffix != '.json' or path.is_symlink() or path == Path(args.input):
            raise ValueError('UNSAFE_JOURNAL')
        existing = json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
        updated, report = update_journal(existing, json.loads(Path(args.input).read_text(encoding='utf-8')))
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix('.json.tmp')
        if temporary.is_symlink():
            raise ValueError('UNSAFE_TEMP')
        with temporary.open('w', encoding='utf-8') as f:
            f.write(json.dumps(updated, indent=2) + '\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
        print(json.dumps(report)); return 0
    except (ValueError, OSError, TypeError, KeyError, ArithmeticError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(exc), 'orders_sent': 0})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
