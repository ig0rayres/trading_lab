"""Read-only bridge: Alpaca reconcile report → Postgres paper_fills. Never authorizes orders."""
from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from typing import Any


def _price_cents(activity: dict[str, Any]) -> int:
    for key in ('price', 'transaction_price', 'fill_price'):
        if key not in activity:
            continue
        try:
            return int(Decimal(str(activity[key])) * 100)
        except (InvalidOperation, ValueError, TypeError):
            continue
    return 0


def ledger_snapshot(conn_factory=None):
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return None
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                out = {}
                for table in (
                    'signal_events',
                    'risk_decisions',
                    'paper_orders',
                    'paper_fills',
                ):
                    cur.execute(
                        'SELECT COUNT(*) FROM %s WHERE deleted_at IS NULL' % table
                    )
                    out[table] = cur.fetchone()[0]
                cur.execute(
                    "SELECT COUNT(*) FROM risk_decisions WHERE decision = %s AND deleted_at IS NULL",
                    ('rejected',),
                )
                out['risk_rejected'] = cur.fetchone()[0]
                cur.execute(
                    "SELECT COUNT(*) FROM paper_orders WHERE status = %s AND deleted_at IS NULL",
                    ('queued_intent',),
                )
                out['paper_queued_intent'] = cur.fetchone()[0]
        return out
    except Exception:
        return {'status': 'LEDGER_UNAVAILABLE'}


def apply_from_report(report: dict[str, Any], conn_factory=None) -> dict[str, Any]:
    """Link broker activities to existing paper_orders; append paper_fills only."""
    if report.get('mode') != 'READ_ONLY':
        return {'status': 'SKIPPED', 'linked': 0, 'orders_sent': 0}
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return {'status': 'NO_LEDGER_DSN', 'linked': 0, 'orders_sent': 0}
    activities = report.get('activities') or {}
    rows = activities.get('activities') if isinstance(activities, dict) else None
    if not isinstance(rows, list):
        return {'status': 'NO_ACTIVITIES', 'linked': 0, 'orders_sent': 0}
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    linked = skipped = 0
    try:
        from ledger_store import insert_row

        with conn_factory() as conn:
            for act in rows:
                if not isinstance(act, dict):
                    skipped += 1
                    continue
                fill_id = str(act.get('id') or '').strip()
                sym = str(act.get('symbol') or '').upper()[:32]
                if not fill_id or not sym:
                    skipped += 1
                    continue
                with conn.cursor() as cur:
                    cur.execute(
                        'SELECT id FROM paper_fills WHERE broker_fill_id = %s',
                        (fill_id,),
                    )
                    if cur.fetchone():
                        skipped += 1
                        continue
                    cur.execute(
                        'SELECT po.id FROM paper_orders po '
                        'LEFT JOIN paper_fills pf ON pf.paper_order_id = po.id '
                        'WHERE po.symbol = %s AND po.deleted_at IS NULL AND pf.id IS NULL '
                        'ORDER BY po.created_at ASC LIMIT 1',
                        (sym,),
                    )
                    po_row = cur.fetchone()
                if not po_row:
                    skipped += 1
                    continue
                qty = act.get('qty') or act.get('quantity') or 1
                insert_row(
                    conn,
                    'paper_fills',
                    {
                        'paper_order_id': po_row[0],
                        'broker_fill_id': fill_id,
                        'qty': qty,
                        'price_cents': _price_cents(act),
                    },
                )
                linked += 1
            conn.commit()
    except Exception as exc:
        return {'status': 'ERROR', 'error_type': type(exc).__name__, 'linked': linked, 'orders_sent': 0}
    return {
        'status': 'APPLIED_READ_ONLY',
        'linked': linked,
        'skipped': skipped,
        'broker_reconciled': False,
        'orders_sent': 0,
    }
