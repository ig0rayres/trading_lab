"""Risk anchors from panel control_flags; tight coded ceiling when DB is unavailable."""
from __future__ import annotations

import os
from decimal import Decimal
from typing import Any, Callable

TIGHT_DEFAULTS: dict[str, Any] = {
    'capital_cents': 500_000,
    'max_risk_per_trade_cents': 5_000,
    'max_open_positions': 3,
    'max_aggregate_risk_cents': 20_000,
    'max_daily_loss_cents': 20_000,
    'max_weekly_loss_cents': 50_000,
    'prodigy_risk_cents': 2_000,
    'demo_operation_on': False,
    'kill_switch_on': False,
}

_FETCH_SQL = (
    'SELECT kill_switch_on, demo_operation_on, capital_cents, max_risk_per_trade_cents, '
    'max_open_positions, max_aggregate_risk_cents, max_daily_loss_cents, '
    'max_weekly_loss_cents, prodigy_risk_cents '
    'FROM control_flags WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 1'
)


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def brl_from_cents(cents: int) -> Decimal:
    return Decimal(cents) / Decimal(100)


def merge_row(row: tuple[Any, ...] | None) -> dict[str, Any]:
    out = dict(TIGHT_DEFAULTS)
    if not row:
        return out
    keys = (
        'kill_switch_on',
        'demo_operation_on',
        'capital_cents',
        'max_risk_per_trade_cents',
        'max_open_positions',
        'max_aggregate_risk_cents',
        'max_daily_loss_cents',
        'max_weekly_loss_cents',
        'prodigy_risk_cents',
    )
    for idx, key in enumerate(keys):
        raw = row[idx]
        if key in ('kill_switch_on', 'demo_operation_on'):
            out[key] = bool(raw) if raw is not None else out[key]
        elif raw is not None:
            out[key] = _coerce_int(raw, int(TIGHT_DEFAULTS[key]))
    return out


def fetch_control_flags(
    *,
    conn_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return dict(TIGHT_DEFAULTS)
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(_FETCH_SQL)
                row = cur.fetchone()
        return merge_row(row)
    except Exception:
        return dict(TIGHT_DEFAULTS)


def demo_send_allowed(
    *,
    conn_factory: Callable[..., Any] | None = None,
) -> tuple[bool, str | None]:
    flags = fetch_control_flags(conn_factory=conn_factory)
    if flags.get('demo_operation_on') is True:
        return True, None
    return False, 'DEMO_OPERATION_OFF'
