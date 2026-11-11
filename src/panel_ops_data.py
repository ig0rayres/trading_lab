"""Operational panel data: signals, performance, blocked-signal context. No broker calls."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable

GATE_A_REJECT_CODES = frozenset({
    'AUTH_FAILED', 'INVALID_SCHEMA', 'INVALID_PROVIDER', 'INVALID_SYMBOL',
    'EXPIRED_OR_FUTURE_SIGNAL', 'DUPLICATE_IGNORED',
})
ANCHOR_FIELD_BY_REJECT = {
    'MAX_POSITIONS': 'max_open_positions',
    'MAX_DAILY_LOSS': 'max_daily_loss_cents',
    'MAX_WEEKLY_LOSS': 'max_weekly_loss_cents',
    'LOSS_DAILY': 'max_daily_loss_cents',
    'LOSS_WEEKLY': 'max_weekly_loss_cents',
    'KILL_SWITCH': 'kill_switch_on',
}
EXCLUDED_PNL_ORDER_STATUSES = frozenset({
    'new', 'accepted', 'queued_intent', 'pending_new', 'pending_replace',
})
PERFORMANCE_LABEL_GROSS = 'gross_unverified_costs'


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        try:
            item = json.loads(line)
            if isinstance(item, dict):
                rows.append(item)
        except (ValueError, TypeError):
            continue
    return rows


def signal_destination(
    *,
    event_status: str | None,
    reject_code: str | None = None,
    paper_status: str | None = None,
    gateway_status: str | None = None,
) -> str:
    if reject_code or (event_status or '').lower() == 'rejected':
        return 'blocked'
    if paper_status in EXCLUDED_PNL_ORDER_STATUSES or gateway_status == 'QUEUED':
        return 'queue'
    if paper_status in ('filled', 'partially_filled', 'MONITORED'):
        return 'order'
    if (event_status or '').lower() == 'accepted':
        return 'queue'
    return 'blocked'


def classify_gate(reject_code: str | None, *, has_risk_row: bool = False) -> str | None:
    if not reject_code:
        return None
    if reject_code in GATE_A_REJECT_CODES or not has_risk_row:
        return 'gate_a'
    return 'gate_b'


def blocked_context(reject_code: str | None, flags: dict[str, Any] | None) -> dict[str, Any] | None:
    if not reject_code:
        return None
    flags = flags or {}
    anchor_field = ANCHOR_FIELD_BY_REJECT.get(reject_code)
    gate = classify_gate(reject_code, has_risk_row=anchor_field is not None)
    ctx: dict[str, Any] = {'gate': gate, 'reject_code': reject_code}
    if anchor_field and anchor_field in flags:
        ctx['anchor_field'] = anchor_field
        ctx['anchor_value'] = flags[anchor_field]
    elif reject_code == 'KILL_SWITCH':
        ctx['anchor_field'] = 'kill_switch_on'
        ctx['anchor_value'] = flags.get('kill_switch_on', True)
    return ctx


def normalize_signal_row(
    row: dict[str, Any],
    *,
    flags: dict[str, Any] | None = None,
    paper_status: str | None = None,
) -> dict[str, Any]:
    reject = row.get('reject_code')
    dest = signal_destination(
        event_status=str(row.get('status') or ''),
        reject_code=str(reject) if reject else None,
        paper_status=paper_status,
        gateway_status=row.get('gateway_status'),
    )
    out = {
        'origin': row.get('source') or row.get('provider') or 'unknown',
        'symbol': row.get('symbol'),
        'market': row.get('market') or 'US_EQUITY',
        'destination': dest,
        'reject_reason': reject or row.get('reason'),
        'received_at': row.get('received_at') or row.get('at'),
        'is_fill': False,
        'label': 'signal_event_not_fill',
    }
    if dest == 'blocked':
        ctx = blocked_context(str(reject) if reject else 'BLOCKED', flags)
        if ctx:
            out['block_detail'] = ctx
    return out


def signals_from_reports(root: Path, *, limit: int = 50) -> list[dict[str, Any]]:
    root = Path(root)
    rows = read_jsonl(root / 'webhooks' / 'journal.jsonl')
    items: list[dict[str, Any]] = []
    for row in reversed(rows[-limit:]):
        payload = row.get('payload') if isinstance(row.get('payload'), dict) else row
        result = row.get('result') if isinstance(row.get('result'), dict) else {}
        merged = {
            'source': payload.get('provider') or 'tradingview',
            'symbol': payload.get('symbol'),
            'market': payload.get('market') or 'US_EQUITY',
            'status': result.get('status') or row.get('status') or 'received',
            'reject_code': result.get('reject_code') or result.get('reason'),
            'received_at': row.get('received_at') or row.get('ts'),
            'gateway_status': result.get('status'),
        }
        items.append(normalize_signal_row(merged))
    return list(reversed(items))


def prodigy_copied_signals(root: Path) -> list[dict[str, Any]]:
    root = Path(root)
    copied: list[dict[str, Any]] = []
    for row in read_jsonl(root / 'evolution' / 'decisions.jsonl'):
        if row.get('kind') != 'signal_copy':
            continue
        copied.append({
            'provider': row.get('provider'),
            'symbol': row.get('symbol'),
            'signal_id': row.get('signal_id'),
            'label': 'research_copy_not_order_auth',
        })
    return copied[-20:]


def _decimal_sum(values: list[Decimal]) -> str | None:
    if not values:
        return None
    return str(sum(values, Decimal(0)))


def performance_from_snapshots(root: Path) -> dict[str, Any]:
    root = Path(root)
    snaps = read_jsonl(root / 'paper' / 'order-snapshots.jsonl')
    latest: dict[str, dict[str, Any]] = {}
    for snap in snaps:
        key = snap.get('client_order_id')
        if key and snap.get('status') == 'MONITORED':
            latest[key] = snap
    by_strategy: dict[str, Decimal] = {}
    total = Decimal(0)
    counted = 0
    for snap in latest.values():
        broker_status = str(snap.get('broker_status') or snap.get('alpaca_status') or '').lower()
        if broker_status in EXCLUDED_PNL_ORDER_STATUSES:
            continue
        try:
            entry = Decimal(str(snap.get('entry_qty') or 0))
            raw_remaining = snap.get('remaining_qty')
            remaining = Decimal(str(entry if raw_remaining is None else raw_remaining))
        except (InvalidOperation, TypeError):
            continue
        if entry <= 0 or remaining != 0:
            continue
        if not snap.get('broker_fill_confirmed') and not snap.get('fill_qty'):
            continue
        try:
            pnl = Decimal(str(snap['realized_gross_pnl_usd']))
        except (InvalidOperation, KeyError, TypeError):
            continue
        strategy = str(snap.get('strategy_key') or 'unknown')
        by_strategy[strategy] = by_strategy.get(strategy, Decimal(0)) + pnl
        total += pnl
        counted += 1
    return {
        'schema_version': 'panel-performance-v1',
        'source': 'confirmed_fills_only',
        'total_gross_usd': str(total) if counted else None,
        'pnl_label': PERFORMANCE_LABEL_GROSS,
        'strategies': [
            {'strategy_key': key, 'gross_usd': str(val), 'pnl_label': PERFORMANCE_LABEL_GROSS}
            for key, val in sorted(by_strategy.items())
        ],
        'excluded_order_statuses': sorted(EXCLUDED_PNL_ORDER_STATUSES),
        'orders_included': counted,
    }


def performance_from_ledger(conn_factory: Callable[..., Any]) -> dict[str, Any] | None:
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT rd.strategy_key, le.amount_cents, po.status '
                    'FROM ledger_entries le '
                    'JOIN paper_fills pf ON pf.id = le.paper_fill_id AND pf.deleted_at IS NULL '
                    'JOIN paper_orders po ON po.id = pf.paper_order_id AND po.deleted_at IS NULL '
                    'JOIN risk_decisions rd ON rd.id = po.risk_decision_id AND rd.deleted_at IS NULL '
                    'WHERE le.deleted_at IS NULL AND le.kind = %s',
                    ('fill',),
                )
                rows = cur.fetchall()
    except Exception:
        return None
    by_strategy: dict[str, int] = {}
    total = 0
    counted = 0
    for strategy_key, amount_cents, status in rows:
        if str(status) in EXCLUDED_PNL_ORDER_STATUSES:
            continue
        cents = int(amount_cents or 0)
        key = str(strategy_key or 'unknown')
        by_strategy[key] = by_strategy.get(key, 0) + cents
        total += cents
        counted += 1
    return {
        'schema_version': 'panel-performance-v1',
        'source': 'ledger_confirmed_fills',
        'total_gross_brl_cents': total if counted else None,
        'pnl_label': PERFORMANCE_LABEL_GROSS,
        'strategies': [
            {
                'strategy_key': key,
                'gross_brl_cents': val,
                'pnl_label': PERFORMANCE_LABEL_GROSS,
            }
            for key, val in sorted(by_strategy.items())
        ],
        'excluded_order_statuses': sorted(EXCLUDED_PNL_ORDER_STATUSES),
        'orders_included': counted,
    }


def load_panel_signals(root: Path, conn_factory: Callable[..., Any] | None, flags: dict[str, Any] | None):
    from_db = []
    if conn_factory is not None:
        try:
            with conn_factory() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        'SELECT source, symbol, market, status, reject_code, received_at '
                        'FROM signal_events WHERE deleted_at IS NULL '
                        'ORDER BY received_at DESC LIMIT 50'
                    )
                    for source, symbol, market, status, reject_code, received_at in cur.fetchall():
                        from_db.append(
                            normalize_signal_row(
                                {
                                    'source': source,
                                    'symbol': symbol,
                                    'market': market,
                                    'status': status,
                                    'reject_code': reject_code,
                                    'received_at': received_at.isoformat()
                                    if isinstance(received_at, datetime)
                                    else received_at,
                                },
                                flags=flags,
                            )
                        )
        except Exception:
            from_db = []
    if from_db:
        return from_db
    return signals_from_reports(root)


def build_panel_bundle(root: Path, conn_factory: Callable[..., Any] | None = None) -> dict[str, Any]:
    flags = None
    if conn_factory is not None:
        try:
            from risk_control_flags import fetch_control_flags

            flags = fetch_control_flags(conn_factory=conn_factory)
        except Exception:
            flags = None
    perf = performance_from_ledger(conn_factory) if conn_factory else None
    if perf is None:
        perf = performance_from_snapshots(root)
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'signals': load_panel_signals(root, conn_factory, flags),
        'prodigy': {
            'ranking': None,
            'copied_signals': prodigy_copied_signals(root),
            'disclaimer': 'research_only_not_order_auth',
        },
        'performance': perf,
        'live_trading_ui': {'enabled': False, 'control_visible': False},
    }
