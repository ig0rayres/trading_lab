"""Daily/weekly loss anchor from confirmed BRL ledger entries only. No invented FX."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

REJECT_UNCONVERTED = 'UNCONVERTED_FILL'
DAILY_LOSS_HALT = 'DAILY_LOSS_HALT'
WEEKLY_LOSS_HALT = 'WEEKLY_LOSS_HALT'


def _halt_state_path() -> Path:
    return Path(os.environ.get('LOSS_PERIOD_HALT_FILE', '/app/reports/paper/loss_period_halts.json'))


def _parse_utc_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _read_halt_state() -> dict[str, str]:
    path = _halt_state_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: str(v) for k, v in data.items() if k in ('daily_until', 'weekly_until') and v}


def _write_halt_state(state: dict[str, str]) -> None:
    path = _halt_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def _sync_period_halts(
    anchor: dict[str, Any],
    *,
    conn_factory=None,
    now_utc: datetime,
) -> dict[str, Any]:
    from risk_control_flags import brl_from_cents, fetch_control_flags

    flags = fetch_control_flags(conn_factory=conn_factory)
    max_daily = brl_from_cents(int(flags['max_daily_loss_cents']))
    max_weekly = brl_from_cents(int(flags['max_weekly_loss_cents']))
    state = _read_halt_state()
    now = now_utc.astimezone(timezone.utc)
    if anchor.get('daily_pnl_verified') and anchor.get('weekly_pnl_verified'):
        daily = Decimal(str(anchor.get('daily_pnl_brl') or '0'))
        weekly = Decimal(str(anchor.get('weekly_pnl_brl') or '0'))
        if daily <= -max_daily:
            state['daily_until'] = (_utc_day_start(now) + timedelta(days=1)).isoformat()
        if weekly <= -max_weekly:
            state['weekly_until'] = (_utc_week_start(now) + timedelta(days=7)).isoformat()
    for key in ('daily_until', 'weekly_until'):
        until = state.get(key)
        if until and _parse_utc_iso(until) <= now:
            state.pop(key, None)
    if state:
        _write_halt_state(state)
    elif _halt_state_path().is_file():
        try:
            _halt_state_path().unlink()
        except OSError:
            pass
    daily_active = bool(state.get('daily_until') and _parse_utc_iso(state['daily_until']) > now)
    weekly_active = bool(state.get('weekly_until') and _parse_utc_iso(state['weekly_until']) > now)
    return {
        'daily_loss_halt_active': daily_active,
        'weekly_loss_halt_active': weekly_active,
        'daily_halt_until_utc': state.get('daily_until'),
        'weekly_halt_until_utc': state.get('weekly_until'),
    }


def _utc_day_start(now: datetime) -> datetime:
    cur = now.astimezone(timezone.utc)
    return cur.replace(hour=0, minute=0, second=0, microsecond=0)


def _utc_week_start(now: datetime) -> datetime:
    day = _utc_day_start(now)
    return day - timedelta(days=day.weekday())


def _brl_from_cents(value: int | None) -> Decimal:
    if value is None:
        raise ValueError('missing amount_cents')
    return Decimal(value) / Decimal(100)


def build_anchor_state(
    ledger_rows: list[dict[str, Any]],
    pending_unconverted: list[dict[str, Any]],
    *,
    now_utc: datetime,
) -> dict[str, Any]:
    day_start = _utc_day_start(now_utc)
    week_start = _utc_week_start(now_utc)
    daily = Decimal(0)
    weekly = Decimal(0)
    for row in ledger_rows:
        cents = row.get('amount_cents')
        if cents is None:
            continue
        created = row['created_at']
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        else:
            created = created.astimezone(timezone.utc)
        amount = _brl_from_cents(int(cents))
        if created >= week_start:
            weekly += amount
        if created >= day_start:
            daily += amount
    blocks = bool(pending_unconverted)
    reject = REJECT_UNCONVERTED if blocks else None
    return {
        'daily_pnl_brl': str(daily),
        'weekly_pnl_brl': str(weekly),
        'daily_pnl_verified': True,
        'weekly_pnl_verified': True,
        'blocks_new_order': blocks,
        'reject_code': reject,
        'unconverted_fill_count': len(pending_unconverted),
    }


def _fetch_rows(conn) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ledger_rows: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    with conn.cursor() as cur:
        cur.execute(
            'SELECT le.amount_cents, le.created_at '
            'FROM ledger_entries le '
            'JOIN paper_fills pf ON pf.id = le.paper_fill_id '
            "WHERE le.deleted_at IS NULL AND pf.deleted_at IS NULL AND le.kind = 'fill'"
        )
        for amount_cents, created_at in cur.fetchall():
            ledger_rows.append({'amount_cents': amount_cents, 'created_at': created_at})
        cur.execute(
            'SELECT pf.id, COALESCE(pf.quote_currency, %s) AS quote_currency '
            'FROM paper_fills pf '
            'WHERE pf.deleted_at IS NULL '
            'AND COALESCE(pf.quote_currency, %s) <> %s '
            'AND NOT EXISTS ('
            '  SELECT 1 FROM ledger_entries le '
            '  WHERE le.paper_fill_id = pf.id AND le.deleted_at IS NULL '
            '  AND le.amount_cents IS NOT NULL'
            ')',
            ('USD', 'USD', 'BRL'),
        )
        for fill_id, quote_currency in cur.fetchall():
            pending.append({'paper_fill_id': str(fill_id), 'quote_currency': quote_currency})
    return ledger_rows, pending


def loss_anchor_snapshot(
    *,
    conn_factory: Callable[..., Any] | None = None,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return {
            'daily_pnl_brl': None,
            'weekly_pnl_brl': None,
            'daily_pnl_verified': False,
            'weekly_pnl_verified': False,
            'blocks_new_order': False,
            'reject_code': None,
        }
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    now = now_utc or datetime.now(timezone.utc)
    try:
        with conn_factory() as conn:
            rows, pending = _fetch_rows(conn)
    except Exception:
        return {
            'daily_pnl_brl': None,
            'weekly_pnl_brl': None,
            'daily_pnl_verified': False,
            'weekly_pnl_verified': False,
            'blocks_new_order': True,
            'reject_code': 'LOSS_DATA_NOT_VERIFIED',
        }
    return build_anchor_state(rows, pending, now_utc=now)


def gate_b_loss_reject(
    *,
    conn_factory: Callable[..., Any] | None = None,
    now_utc: datetime | None = None,
) -> str | None:
    now = now_utc or datetime.now(timezone.utc)
    snap = loss_anchor_snapshot(conn_factory=conn_factory, now_utc=now)
    if snap.get('blocks_new_order'):
        return snap.get('reject_code') or REJECT_UNCONVERTED
    halts = _sync_period_halts(snap, conn_factory=conn_factory, now_utc=now)
    if halts.get('daily_loss_halt_active'):
        return DAILY_LOSS_HALT
    if halts.get('weekly_loss_halt_active'):
        return WEEKLY_LOSS_HALT
    return None


def portfolio_risk_snapshot(
    *,
    conn_factory: Callable[..., Any] | None = None,
    now_utc: datetime | None = None,
    available_cash_brl: str | None = None,
) -> dict[str, Any]:
    now = now_utc or datetime.now(timezone.utc)
    anchor = loss_anchor_snapshot(conn_factory=conn_factory, now_utc=now)
    if available_cash_brl is None:
        from risk_control_flags import brl_from_cents, fetch_control_flags

        cash = brl_from_cents(int(fetch_control_flags(conn_factory=conn_factory)['capital_cents']))
        available_cash_brl = str(cash)
    verified = anchor.get('daily_pnl_verified') is True and anchor.get('weekly_pnl_verified') is True
    halts = _sync_period_halts(anchor, conn_factory=conn_factory, now_utc=now)
    return {
        'complete': verified and not halts.get('daily_loss_halt_active') and not halts.get('weekly_loss_halt_active'),
        'daily_pnl_verified': anchor.get('daily_pnl_verified'),
        'weekly_pnl_verified': anchor.get('weekly_pnl_verified'),
        'broker_reconciled': verified and not anchor.get('blocks_new_order'),
        'positions': [],
        'daily_pnl_brl': anchor.get('daily_pnl_brl') or '0',
        'weekly_pnl_brl': anchor.get('weekly_pnl_brl') or '0',
        'available_cash_brl': available_cash_brl,
        'has_pending_orders': False,
        **halts,
    }