"""Seed operational ON defaults after migrate; never undo operator trigger_changes."""
from __future__ import annotations

from datetime import datetime, timezone

VALID_MARKETS = ('B3_EQUITY', 'CRYPTO', 'FOREX')

_BOOTSTRAP_FLAGS = {
    'kill_switch_on': False,
    'demo_operation_on': True,
    'max_risk_per_trade_cents': 5000,
    'prodigy_risk_cents': 2000,
    'capital_cents': 500000,
    'max_open_positions': 3,
    'max_aggregate_risk_cents': 20000,
    'max_daily_loss_cents': 20000,
    'max_weekly_loss_cents': 50000,
}


def _operator_touched(cur, target_table: str, target_id, field_name: str) -> bool:
    cur.execute(
        'SELECT 1 FROM trigger_changes WHERE deleted_at IS NULL '
        'AND target_table = %s AND target_id = %s AND field_name = %s LIMIT 1',
        (target_table, target_id, field_name),
    )
    return cur.fetchone() is not None


def ensure_operational_defaults(conn) -> dict[str, int]:
    """Apply ON-by-default policy for untouched rows. Returns counters for logging."""
    changed = {'control_flags': 0, 'market_controls': 0, 'inserted_flags': 0}
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id, kill_switch_on, demo_operation_on FROM control_flags '
            'WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 1'
        )
        row = cur.fetchone()
        now = datetime.now(timezone.utc)
        if row is None:
            b = _BOOTSTRAP_FLAGS
            cur.execute(
                'INSERT INTO control_flags (kill_switch_on, demo_operation_on, '
                'max_risk_per_trade_cents, prodigy_risk_cents, capital_cents, '
                'max_open_positions, max_aggregate_risk_cents, max_daily_loss_cents, '
                'max_weekly_loss_cents, created_at, updated_at) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (
                    b['kill_switch_on'], b['demo_operation_on'],
                    b['max_risk_per_trade_cents'], b['prodigy_risk_cents'],
                    b['capital_cents'], b['max_open_positions'],
                    b['max_aggregate_risk_cents'], b['max_daily_loss_cents'],
                    b['max_weekly_loss_cents'], now, now,
                ),
            )
            changed['inserted_flags'] = 1
        else:
            row_id, kill_on, demo_on = row[0], row[1], row[2]
            if demo_on is False and not _operator_touched(cur, 'control_flags', row_id, 'demo_operation_on'):
                cur.execute(
                    'UPDATE control_flags SET demo_operation_on = true, updated_at = %s WHERE id = %s',
                    (now, row_id),
                )
                changed['control_flags'] += 1
            if kill_on is True and not _operator_touched(cur, 'control_flags', row_id, 'kill_switch_on'):
                cur.execute(
                    'UPDATE control_flags SET kill_switch_on = false, updated_at = %s WHERE id = %s',
                    (now, row_id),
                )
                changed['control_flags'] += 1

        for market in VALID_MARKETS:
            cur.execute(
                'SELECT id, operation_on FROM market_controls '
                'WHERE deleted_at IS NULL AND market = %s',
                (market,),
            )
            mrow = cur.fetchone()
            if mrow is None:
                continue
            m_id, op_on = mrow[0], mrow[1]
            if op_on is False and not _operator_touched(cur, 'market_controls', m_id, 'operation_on'):
                cur.execute(
                    'UPDATE market_controls SET operation_on = true, updated_at = %s WHERE id = %s',
                    (now, m_id),
                )
                changed['market_controls'] += 1
    return changed