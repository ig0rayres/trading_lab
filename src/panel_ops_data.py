"""Operational panel data: signals, performance, blocked-signal context. No broker calls."""
from __future__ import annotations

import json
import math
import os
import re
from datetime import date, datetime, timezone
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
OPEN_ORDER_BROKER_STATUSES = frozenset({
    'new', 'accepted', 'pending_new', 'pending_replace', 'partially_filled',
})
PERFORMANCE_LABEL_GROSS = 'gross_unverified_costs'
SIGNAL_COPY_STRATEGY_KEY = 'signal_copy'
PROVENANCE_UNKNOWN_ORIGIN = 'origem desconhecida'
PROVENANCE_UNKNOWN_SIGNAL = 'sem vínculo com sinal'
INVENTORY_EMPTY_PT = 'Nenhum sinal neste inventário.'
PRODIGY_POOL_EMPTY_PT = 'Nenhum candidato de pesquisa no pool.'
_CANDIDATES_REFRESH_FILENAME = 'candidates-refresh-latest.json'


def _panel_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if type(value).__name__ == 'UUID':
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode('utf-8', errors='replace')
    return str(value)


def _sanitize_order_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _panel_json_value(val) for key, val in row.items()}


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


def latest_monitored_snapshots(root: Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for snap in read_jsonl(Path(root) / 'paper' / 'order-snapshots.jsonl'):
        key = snap.get('client_order_id')
        if key and snap.get('status') == 'MONITORED':
            latest[key] = snap
    return latest


def _snap_qtys(snap: dict[str, Any]) -> tuple[Decimal, Decimal] | None:
    try:
        entry = Decimal(str(snap.get('entry_qty') or 0))
        raw_remaining = snap.get('remaining_qty')
        remaining = Decimal(str(entry if raw_remaining is None else raw_remaining))
        return entry, remaining
    except (InvalidOperation, TypeError):
        return None


def snapshot_is_confirmed_fill(snap: dict[str, Any]) -> bool:
    if str(snap.get('paper_status') or '') == 'queued_intent':
        return False
    broker_status = str(snap.get('broker_status') or snap.get('alpaca_status') or '').lower()
    if broker_status in EXCLUDED_PNL_ORDER_STATUSES:
        return False
    qtys = _snap_qtys(snap)
    if qtys is None:
        return False
    entry, remaining = qtys
    if entry <= 0 or remaining != 0:
        return False
    return bool(snap.get('broker_fill_confirmed') or snap.get('fill_qty'))


def snapshot_is_open_order(snap: dict[str, Any]) -> bool:
    if snapshot_is_confirmed_fill(snap):
        return False
    if str(snap.get('paper_status') or '') == 'queued_intent':
        return True
    qtys = _snap_qtys(snap)
    if qtys is None:
        return False
    entry, remaining = qtys
    if entry > 0 and remaining > 0:
        return True
    broker_status = str(snap.get('broker_status') or snap.get('alpaca_status') or '').lower()
    return broker_status in OPEN_ORDER_BROKER_STATUSES


def _signal_orders_overlay_by_client_id(root: Path) -> dict[str, dict[str, Any]]:
    by_cid: dict[str, dict[str, Any]] = {}
    for rel in ('paper/signal-orders.jsonl', 'reports/paper/signal-orders.jsonl'):
        for row in read_jsonl(Path(root) / rel):
            cid = row.get('client_order_id')
            if not cid:
                continue
            entry: dict[str, Any] = {}
            if row.get('signal_id') is not None:
                entry['signal_id'] = row['signal_id']
            if row.get('provider') is not None:
                entry['provider'] = row['provider']
            if entry:
                by_cid[str(cid)] = entry
    return by_cid


def _apply_ticket_overlay(row: dict[str, Any], overlay: dict[str, dict[str, Any]]) -> None:
    cid = str(row.get('client_order_id') or '')
    journal = overlay.get(cid) or {}
    if journal.get('signal_id') is not None:
        row['signal_id'] = journal['signal_id']
    if row.get('provenance_status') != 'linked' and journal.get('provider'):
        row['origin'] = journal['provider']
        row['provenance_status'] = 'linked'


def _finalize_order_provenance(row: dict[str, Any]) -> dict[str, Any]:
    status = row.get('provenance_status')
    if status != 'linked':
        row['provenance_status'] = 'unknown'
        if not row.get('origin') or row.get('origin') == 'unknown':
            row['origin'] = PROVENANCE_UNKNOWN_ORIGIN
    if not row.get('signal_id'):
        row['signal_link_notice'] = PROVENANCE_UNKNOWN_SIGNAL
    return row


def _decorate_order_rows(
    rows: list[dict[str, Any]],
    overlay: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        _apply_ticket_overlay(item, overlay)
        out.append(_finalize_order_provenance(item))
    return out


def order_row_from_snapshot(snap: dict[str, Any], *, history: bool = False) -> dict[str, Any]:
    row: dict[str, Any] = {
        'client_order_id': snap.get('client_order_id'),
        'symbol': snap.get('symbol'),
        'side': snap.get('side'),
        'status': snap.get('status'),
        'broker_status': snap.get('broker_status') or snap.get('alpaca_status'),
        'paper_status': snap.get('paper_status'),
        'entry_qty': snap.get('entry_qty'),
        'remaining_qty': snap.get('remaining_qty'),
        'strategy_key': snap.get('strategy_key'),
        'broker_order_id': snap.get('broker_order_id'),
        'market': snap.get('market') or 'US_EQUITY',
    }
    if snap.get('origin'):
        row['origin'] = snap.get('origin')
        row['provenance_status'] = 'linked'
    if snap.get('signal_id'):
        row['signal_id'] = snap.get('signal_id')
    if history:
        row['realized_gross_pnl_usd'] = snap.get('realized_gross_pnl_usd')
        row['pnl_label'] = PERFORMANCE_LABEL_GROSS
        row['broker_fill_confirmed'] = snap.get('broker_fill_confirmed')
    return _sanitize_order_row(row)


def open_orders_from_snapshots(root: Path) -> list[dict[str, Any]]:
    overlay = _signal_orders_overlay_by_client_id(root)
    rows = [
        order_row_from_snapshot(snap)
        for snap in latest_monitored_snapshots(root).values()
        if snapshot_is_open_order(snap)
    ]
    rows = _decorate_order_rows(rows, overlay)
    return sorted(rows, key=lambda item: str(item.get('symbol') or ''))


def order_history_from_snapshots(root: Path) -> list[dict[str, Any]]:
    overlay = _signal_orders_overlay_by_client_id(root)
    rows = [
        order_row_from_snapshot(snap, history=True)
        for snap in latest_monitored_snapshots(root).values()
        if snapshot_is_confirmed_fill(snap)
    ]
    rows = _decorate_order_rows(rows, overlay)
    return sorted(rows, key=lambda item: str(item.get('symbol') or ''))


def _ledger_open_order_row(
    cid: Any,
    symbol: Any,
    side: Any,
    status: Any,
    qty: Any,
    broker_id: Any,
    strategy_key: Any,
    signal_source: Any = None,
    signal_event_id: Any = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        'client_order_id': cid,
        'symbol': symbol,
        'side': side,
        'status': status,
        'entry_qty': qty,
        'remaining_qty': qty,
        'broker_order_id': broker_id,
        'strategy_key': strategy_key,
        'market': 'US_EQUITY',
    }
    if signal_source and signal_event_id:
        row['origin'] = signal_source
        row['signal_event_id'] = signal_event_id
        row['provenance_status'] = 'linked'
    return _sanitize_order_row(row)


def open_orders_from_ledger(conn_factory: Callable[..., Any]) -> list[dict[str, Any]] | None:
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT po.client_order_id, po.symbol, po.side, po.status, po.qty, '
                    'po.broker_order_id, rd.strategy_key, se.source, se.id '
                    'FROM paper_orders po '
                    'JOIN risk_decisions rd ON rd.id = po.risk_decision_id AND rd.deleted_at IS NULL '
                    'LEFT JOIN signal_events se ON se.id = rd.signal_event_id AND se.deleted_at IS NULL '
                    'WHERE po.deleted_at IS NULL AND po.status != %s '
                    'ORDER BY po.created_at DESC LIMIT 100',
                    ('filled',),
                )
                fetched = cur.fetchall()
        if not fetched:
            return None
        rows = [
            _ledger_open_order_row(
                cid, symbol, side, status, qty, broker_id, strategy_key, signal_source, signal_event_id,
            )
            for cid, symbol, side, status, qty, broker_id, strategy_key, signal_source, signal_event_id in fetched
            if str(status) != 'filled'
        ]
        return rows or None
    except Exception:
        return None


def _ledger_history_row(
    cid: Any,
    symbol: Any,
    side: Any,
    status: Any,
    broker_id: Any,
    strategy_key: Any,
    qty: Any,
    cents: Any,
    filled_at: Any,
    signal_source: Any = None,
    signal_event_id: Any = None,
) -> dict[str, Any] | None:
    if str(status) in EXCLUDED_PNL_ORDER_STATUSES:
        return None
    gross = None
    if cents is not None:
        gross = str(Decimal(cents) / Decimal(100))
    row: dict[str, Any] = {
        'client_order_id': cid,
        'symbol': symbol,
        'side': side,
        'status': status,
        'broker_order_id': broker_id,
        'strategy_key': strategy_key,
        'entry_qty': qty,
        'remaining_qty': 0,
        'realized_gross_pnl_usd': gross,
        'pnl_label': PERFORMANCE_LABEL_GROSS,
        'broker_fill_confirmed': True,
        'filled_at': filled_at,
        'market': 'US_EQUITY',
    }
    if signal_source and signal_event_id:
        row['origin'] = signal_source
        row['signal_event_id'] = signal_event_id
        row['provenance_status'] = 'linked'
    return _sanitize_order_row(row)


def order_history_from_ledger(conn_factory: Callable[..., Any]) -> list[dict[str, Any]] | None:
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT po.client_order_id, po.symbol, po.side, po.status, po.broker_order_id, '
                    'rd.strategy_key, pf.qty, le.amount_cents, pf.filled_at, se.source, se.id '
                    'FROM paper_fills pf '
                    'JOIN paper_orders po ON po.id = pf.paper_order_id AND po.deleted_at IS NULL '
                    'JOIN risk_decisions rd ON rd.id = po.risk_decision_id AND rd.deleted_at IS NULL '
                    'LEFT JOIN signal_events se ON se.id = rd.signal_event_id AND se.deleted_at IS NULL '
                    'JOIN ledger_entries le ON le.paper_fill_id = pf.id AND le.deleted_at IS NULL '
                    "WHERE pf.deleted_at IS NULL AND le.kind = %s AND po.status NOT IN %s "
                    'ORDER BY pf.filled_at DESC NULLS LAST LIMIT 100',
                    ('fill', tuple(EXCLUDED_PNL_ORDER_STATUSES)),
                )
                fetched = cur.fetchall()
        if not fetched:
            return None
        rows: list[dict[str, Any]] = []
        for row in fetched:
            item = _ledger_history_row(*row)
            if item is not None:
                rows.append(item)
        return rows or None
    except Exception:
        return None


def load_panel_open_orders(root: Path, conn_factory: Callable[..., Any] | None) -> list[dict[str, Any]]:
    overlay = _signal_orders_overlay_by_client_id(root)
    if conn_factory is not None:
        try:
            from_db = open_orders_from_ledger(conn_factory)
            if from_db:
                return _decorate_order_rows(from_db, overlay)
        except Exception:
            pass
    try:
        return open_orders_from_snapshots(root)
    except Exception:
        return []


def load_panel_order_history(root: Path, conn_factory: Callable[..., Any] | None) -> list[dict[str, Any]]:
    overlay = _signal_orders_overlay_by_client_id(root)
    if conn_factory is not None:
        try:
            from_db = order_history_from_ledger(conn_factory)
            if from_db:
                return _decorate_order_rows(from_db, overlay)
        except Exception:
            pass
    try:
        return order_history_from_snapshots(root)
    except Exception:
        return []


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


_TIMESFM_RESEARCH_LABELS = frozenset({'research_tip', 'suggestion'})
_TIMESFM_NOTE_TO_REASON = {
    'TIMESFM_ENABLED off': 'modelo desligado neste ambiente.',
    'TIMESFM_CHECKPOINT unset': 'checkpoint não configurado.',
    'insufficient_context_series': 'série de contexto insuficiente.',
    'runtime_unavailable': 'modelo ou dependência ausente.',
}
def _operator_reason_from_note(note: str | None) -> str:
    raw = (note or '').strip()
    return _TIMESFM_NOTE_TO_REASON.get(raw, 'modelo ou dependência ausente.')


def _read_latest_daily_timesfm(root: Path) -> tuple[dict[str, Any], dict[str, Any]] | None:
    daily_dir = root / 'evolution' / 'daily'
    if not daily_dir.is_dir():
        return None
    daily_files = sorted(daily_dir.glob('*.json'), reverse=True)
    if not daily_files:
        return None
    try:
        payload = json.loads(daily_files[0].read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None
    timesfm = payload.get('timesfm')
    if not isinstance(timesfm, dict):
        return None
    return timesfm, payload


def _cheap_context_series(root: Path) -> list[float]:
    series: list[float] = []
    for row in read_jsonl(root / 'webhooks' / 'journal.jsonl'):
        res = row.get('result') if isinstance(row.get('result'), dict) else {}
        added = False
        for key in ('fill_qty', 'qty', 'score'):
            if key in res:
                try:
                    series.append(float(res[key]))
                    added = True
                except (TypeError, ValueError):
                    pass
                break
        if not added:
            series.append(float(len(series) + 1))
    return series[-64:]


def _sanitize_research_tip(tip: dict[str, Any]) -> dict[str, Any]:
    label = tip.get('label') or 'suggestion'
    if label not in _TIMESFM_RESEARCH_LABELS:
        label = 'suggestion'
    summary = tip.get('summary') or tip.get('note')
    return {
        'label': _panel_json_value(label),
        'kind': _panel_json_value(tip.get('kind')),
        'summary': _panel_json_value(summary),
        'execution_authorized': False,
        'paper_allowed': False,
        'orders_sent': _panel_json_value(tip.get('orders_sent', 0)),
    }


def _append_research_tips(
    dest: list[dict[str, Any]],
    seen: set[tuple[Any, Any]],
    rows: list[Any],
) -> None:
    for tip in rows:
        if not isinstance(tip, dict):
            continue
        if (tip.get('label') or '') not in _TIMESFM_RESEARCH_LABELS:
            continue
        sanitized = _sanitize_research_tip(tip)
        key = (sanitized.get('label'), sanitized.get('summary'))
        if key in seen:
            continue
        seen.add(key)
        dest.append(sanitized)


def _collect_research_tips(
    timesfm: dict[str, Any],
    daily_payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    tips: list[dict[str, Any]] = []
    seen: set[tuple[Any, Any]] = set()
    _append_research_tips(tips, seen, list(timesfm.get('tips') or []))
    if daily_payload:
        _append_research_tips(tips, seen, list(daily_payload.get('tips') or []))
    return tips


def _panel_timesfm_shape(
    *,
    status: str,
    note: str | None,
    tips: list[dict[str, Any]],
) -> dict[str, Any]:
    out: dict[str, Any] = {
        'timesfm_status': status,
        'tips': tips if status == 'OK' else [],
        'operator_reason': _operator_reason_from_note(note),
        'execution_authorized': False,
        'paper_allowed': False,
    }
    if note:
        out['note'] = _panel_json_value(note)
    return out


def load_panel_timesfm(root: Path) -> dict[str, Any]:
    root = Path(root)
    latest = _read_latest_daily_timesfm(root)
    if latest is not None:
        timesfm, payload = latest
        status = str(timesfm.get('timesfm_status') or 'UNAVAILABLE')
        note = timesfm.get('note')
        note_str = str(note) if note is not None else None
        if status == 'OK':
            tips = _collect_research_tips(timesfm, payload)
        else:
            tips = []
        return _panel_timesfm_shape(status=status, note=note_str, tips=tips)
    day = date.today().isoformat()
    try:
        from timesfm_context import build_timesfm_block
    except ImportError:
        return _panel_timesfm_shape(status='UNAVAILABLE', note=None, tips=[])
    block = build_timesfm_block(day=day, context_values=_cheap_context_series(root))
    status = str(block.get('timesfm_status') or 'UNAVAILABLE')
    note = block.get('note')
    note_str = str(note) if note is not None else None
    tips = _collect_research_tips(block, None) if status == 'OK' else []
    return _panel_timesfm_shape(status=status, note=note_str, tips=tips)


def load_panel_strategy_catalog(
    conn_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    try:
        from strategy_catalog import list_strategy_states

        rows = list_strategy_states(conn_factory=conn_factory)
    except ImportError:
        rows = None
    if rows is None:
        return {'status': 'LEDGER_UNAVAILABLE', 'strategies': []}
    strategies: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        strategies.append(
            {
                'strategy_key': _panel_json_value(row.get('strategy_key')),
                'phase': _panel_json_value(row.get('phase')),
                'paper_allowed': bool(row.get('paper_allowed')),
                'promotion': _panel_json_value(row.get('promotion')),
            }
        )
    return {
        'status': 'OK',
        'strategies': strategies,
        'note': 'Phase changes are operator-only; dashboard is read-only.',
    }


def _is_signal_copy_row(row: dict[str, Any]) -> bool:
    return str(row.get('strategy_key') or '') == SIGNAL_COPY_STRATEGY_KEY


def _signal_copy_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if _is_signal_copy_row(row)]


def _copy_providers(research_copies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    providers: list[dict[str, Any]] = []
    for row in research_copies:
        raw = row.get('provider')
        provider = str(raw).strip() if raw is not None else ''
        if not provider or provider in seen:
            continue
        seen.add(provider)
        providers.append({'provider': provider, 'label': 'research_only'})
    return providers


def _copy_performance_slice(perf: dict[str, Any] | None) -> dict[str, Any]:
    base = perf if isinstance(perf, dict) else {}
    strategies = _signal_copy_rows(base.get('strategies') or [])
    total: str | None = None
    if strategies:
        gross_vals: list[Decimal] = []
        for row in strategies:
            try:
                gross_vals.append(Decimal(str(row.get('gross_usd') or 0)))
            except (InvalidOperation, TypeError):
                continue
        total = _decimal_sum(gross_vals)
    return {
        'schema_version': base.get('schema_version'),
        'source': base.get('source'),
        'pnl_label': base.get('pnl_label') or PERFORMANCE_LABEL_GROSS,
        'strategies': strategies,
        'total_gross_usd': total,
        'orders_included': len(strategies) if strategies else 0,
        'excluded_order_statuses': base.get('excluded_order_statuses'),
    }


def _inventory_key(row: dict[str, Any]) -> str | None:
    if row.get('provenance_status') != 'linked':
        return None
    origin = str(row.get('origin') or '')
    sid = row.get('signal_id') or row.get('signal_event_id')
    if not origin or not sid:
        return None
    return f'{origin}|{sid}'


def _inventory_upsert(
    items_map: dict[str, dict[str, Any]],
    row: dict[str, Any],
) -> dict[str, Any] | None:
    key = _inventory_key(row)
    if key is None:
        return None
    if key not in items_map:
        items_map[key] = {
            'origin': row.get('origin'),
            'signal_id': row.get('signal_id'),
            'signal_event_id': row.get('signal_event_id'),
            'provenance_status': 'linked',
            'operating': 0,
            'fills_confirmed': 0,
            'gross_usd_total': None,
            'pnl_label': PERFORMANCE_LABEL_GROSS,
        }
    return items_map[key]


def _build_copy_inventory(
    operating: list[dict[str, Any]],
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    items_map: dict[str, dict[str, Any]] = {}
    unknown_unlinked = 0
    for row in operating:
        if row.get('provenance_status') != 'linked':
            unknown_unlinked += 1
            continue
        entry = _inventory_upsert(items_map, row)
        if entry is None:
            unknown_unlinked += 1
            continue
        entry['operating'] += 1
    for row in history:
        if str(row.get('paper_status') or '') == 'queued_intent':
            continue
        if not row.get('broker_fill_confirmed') and row.get('realized_gross_pnl_usd') is None:
            continue
        if row.get('provenance_status') != 'linked':
            unknown_unlinked += 1
            continue
        entry = _inventory_upsert(items_map, row)
        if entry is None:
            unknown_unlinked += 1
            continue
        try:
            gross = Decimal(str(row.get('realized_gross_pnl_usd') or 0))
        except (InvalidOperation, TypeError):
            gross = Decimal(0)
        entry['fills_confirmed'] += 1
        prior = entry.get('gross_usd_total')
        try:
            prior_dec = Decimal(str(prior)) if prior is not None else Decimal(0)
        except (InvalidOperation, TypeError):
            prior_dec = Decimal(0)
        entry['gross_usd_total'] = str(prior_dec + gross)
    items = sorted(items_map.values(), key=lambda item: str(item.get('origin') or ''))
    return {
        'items': items,
        'unknown_unlinked_count': unknown_unlinked,
        'empty_label': INVENTORY_EMPTY_PT,
        'source': 'confirmed_fills_only',
        'pnl_label': PERFORMANCE_LABEL_GROSS,
    }


PREAPPROVAL_METRIC_KEYS = (
    'win_rate_pct',
    'shrunk_win_rate_pct',
    'profit_factor_reported',
    'reported_pnl_sum',
    'net_return_pct',
    'max_drawdown_pct',
    'prodigy_score',
    'score',
    'status',
    'eligible',
    'copy_approved',
)
PREAPPROVAL_METRICS_LABEL = 'research_only'
_PREAPPROVAL_PLATFORMS = frozenset({'collective2', 'prodigy', 'tradingview'})


def _overlay_research_metrics(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    out: dict[str, Any] = {}
    for key in PREAPPROVAL_METRIC_KEYS:
        if key not in row:
            continue
        val = row[key]
        if val is None:
            continue
        out[key] = _panel_json_value(val)
    return out


def fetch_signal_provider_approvals(conn_factory: Callable[..., Any]) -> list[dict[str, Any]]:
    with conn_factory() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT platform, provider_id, status, source, decided_at '
                'FROM signal_provider_approvals ORDER BY platform, provider_id'
            )
            rows = []
            for platform, provider_id, status, source, decided_at in cur.fetchall():
                rows.append(
                    {
                        'platform': platform,
                        'provider_id': provider_id,
                        'status': status,
                        'source': source,
                        'decided_at': decided_at.isoformat()
                        if isinstance(decided_at, datetime)
                        else decided_at,
                    }
                )
            return rows


def upsert_signal_provider_approval(
    conn_factory: Callable[..., Any],
    platform: str,
    provider_id: str,
    action: str,
) -> dict[str, Any]:
    plat = str(platform or '').strip().lower()
    pid = str(provider_id or '').strip()
    if plat not in _PREAPPROVAL_PLATFORMS or not pid:
        raise ValueError('INVALID_BODY')
    if plat == 'collective2' and not _C2_NAMED_ID_RE.match(pid):
        raise ValueError('INVALID_BODY')
    if action not in ('approve', 'reject'):
        raise ValueError('INVALID_BODY')
    status = 'approved' if action == 'approve' else 'rejected'
    with conn_factory() as conn:
        with conn.cursor() as cur:
            cur.execute(
                '''
                INSERT INTO signal_provider_approvals (
                    platform, provider_id, status, source, decided_at
                ) VALUES (%s, %s, %s, 'panel', now())
                ON CONFLICT (platform, provider_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    source = 'panel',
                    decided_at = now(),
                    updated_at = now()
                ''',
                (plat, pid, status),
            )
        conn.commit()
    return {'platform': plat, 'provider_id': pid, 'status': status, 'source': 'panel'}


def _provider_approval_map(
    conn_factory: Callable[..., Any] | None,
) -> dict[tuple[str, str], dict[str, Any]]:
    if conn_factory is None:
        return {}
    try:
        rows = fetch_signal_provider_approvals(conn_factory)
    except Exception:
        return {}
    return {(str(r['platform']), str(r['provider_id'])): r for r in rows}


def _c2_seed_source_for_id(root: Path, provider_id: str) -> str:
    env_ids = set(_c2_approved_ids_from_env())
    if provider_id in env_ids:
        return 'seed_env'
    for path in _load_c2_allowlist_config_paths(root):
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(payload, dict):
            continue
        if provider_id in _parse_numeric_ids(payload.get('approved_ids')):
            return 'seed_json'
    return 'seed_json'


def resolve_c2_paper_copy_approved_ids(
    root: Path,
    conn_factory: Callable[..., Any] | None,
) -> list[str]:
    seed = load_c2_paper_copy_approved_ids(root)
    ledger = _provider_approval_map(conn_factory)
    approved: set[str] = set()
    for (plat, pid), row in ledger.items():
        if plat == 'collective2' and row.get('status') == 'approved':
            approved.add(pid)
    for pid in seed:
        key = ('collective2', pid)
        row = ledger.get(key)
        if row and row.get('status') == 'rejected':
            continue
        if row and row.get('status') == 'approved':
            continue
        if row and row.get('status') == 'pending':
            continue
        if row is None:
            approved.add(pid)
    return sorted(
        approved,
        key=lambda x: (not str(x).isdigit(), int(x) if str(x).isdigit() else 0, str(x)),
    )


def persist_candidates_refresh(root: Path, record: dict[str, Any]) -> None:
    intel = Path(root) / 'intelligence'
    intel.mkdir(parents=True, exist_ok=True)
    path = intel / _CANDIDATES_REFRESH_FILENAME
    path.write_text(json.dumps(record, indent=2), encoding='utf-8')


def load_candidates_refresh(root: Path) -> dict[str, Any] | None:
    path = Path(root) / 'intelligence' / _CANDIDATES_REFRESH_FILENAME
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return None
    return payload if isinstance(payload, dict) else None


def _load_c2_research_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rel in (
        'intelligence/provider-research-top10-latest.json',
        'reports/intelligence/provider-research-top10-latest.json',
    ):
        path = Path(root) / rel
        if not path.is_file():
            path = _repo_config_root() / rel
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get('mode') == 'PRODIGY_RANK_RESEARCH_ONLY':
            continue
        for row in payload.get('top_10_research') or []:
            if isinstance(row, dict):
                rows.append(dict(row))
        if rows:
            break
    return rows


def _prodigy_rank_json_path(root: Path) -> Path | None:
    for candidate in (
        Path(root) / 'intelligence' / 'prodigy-top10-latest.json',
        _repo_config_root() / 'intelligence' / 'prodigy-top10-latest.json',
    ):
        if candidate.is_file():
            return candidate
    return None


def _read_prodigy_rank_payload(root: Path) -> dict[str, Any] | None:
    path = _prodigy_rank_json_path(root)
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return None
    if not isinstance(payload, dict) or payload.get('mode') != 'PRODIGY_RANK_RESEARCH_ONLY':
        return None
    return payload


def _load_prodigy_rank_provider_rows(root: Path) -> list[dict[str, Any]]:
    payload = _read_prodigy_rank_payload(root)
    if not payload:
        return []
    providers = payload.get('providers')
    if isinstance(providers, list) and providers:
        return [dict(row) for row in providers if isinstance(row, dict)]
    top = payload.get('top_10_research')
    if isinstance(top, list):
        return [dict(row) for row in top if isinstance(row, dict)]
    return []


def _load_prodigy_research_rows(root: Path) -> list[dict[str, Any]]:
    return _load_prodigy_rank_provider_rows(root)


def _providers_raw_dir(root: Path) -> Path:
    return Path(root) / 'providers' / 'raw'


def discover_c2_strategy_ids_from_raw(root: Path) -> list[str]:
    raw_dir = _providers_raw_dir(root)
    if not raw_dir.is_dir():
        return []
    seen: set[str] = set()
    ids: list[str] = []
    for path in raw_dir.glob('*_closed_trades.json'):
        prefix = path.name.split('_', 1)[0]
        if not prefix.isdigit() or prefix in seen:
            continue
        seen.add(prefix)
        ids.append(prefix)
    return sorted(ids, key=int)


def _prodigy_research_row_by_id(root: Path) -> dict[str, dict[str, Any]]:
    rows = _load_prodigy_research_rows(root)
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        pid = row.get('provider_id') or row.get('provider')
        if pid is not None:
            out[str(pid).strip()] = row
    return out


def _c2_scan_strategy_ids(root: Path) -> set[str]:
    for rel in (
        Path(root) / 'intelligence' / 'c2_search_strategies_latest.json',
        _providers_raw_dir(root) / 'c2_search_strategies_latest.json',
    ):
        if not rel.is_file():
            continue
        try:
            payload = json.loads(rel.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            continue
        raw = payload.get('raw') if isinstance(payload, dict) else {}
        if not isinstance(raw, dict):
            continue
        found: set[str] = set()
        for row in raw.get('Results') or []:
            if not isinstance(row, dict):
                continue
            sid = row.get('StrategyId')
            if sid is None:
                continue
            try:
                found.add(str(int(sid)))
            except (TypeError, ValueError):
                continue
        if found:
            return found
    return set()


def _c2_raw_closed_trades_results_empty(root: Path, provider_id: str) -> bool:
    path = _providers_raw_dir(root) / f'{provider_id}_closed_trades.json'
    if not path.is_file():
        return True
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return True
    raw = payload.get('raw') if isinstance(payload, dict) else {}
    results = raw.get('Results') if isinstance(raw, dict) else None
    return not results


def _unique_tradingview_origins(signals: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    origins: list[str] = []
    for row in signals:
        if not isinstance(row, dict):
            continue
        origin = str(row.get('origin') or row.get('source') or '').strip()
        if not origin or origin.lower() == 'unknown':
            continue
        key = origin.lower()
        if key in seen:
            continue
        seen.add(key)
        origins.append(origin)
    return sorted(origins, key=str.lower)


def build_preapproval_queue(
    root: Path,
    conn_factory: Callable[..., Any] | None,
    signals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    del signals
    from prodigy_rank import is_pearl_candidate, pearl_sort_key

    ledger = _provider_approval_map(conn_factory)
    pearls = [dict(row) for row in _load_prodigy_rank_provider_rows(root) if is_pearl_candidate(row)]
    pearls.sort(key=pearl_sort_key)
    queue: list[dict[str, Any]] = []
    for row in pearls[:10]:
        pid = str(row.get('provider_id') or row.get('provider') or '').strip()
        if not pid:
            continue
        key = ('prodigy', pid)
        ledger_row = ledger.get(key)
        if ledger_row:
            status = ledger_row['status']
            source = ledger_row['source']
        else:
            status = 'pending'
            source = 'prodigy_rank'
        queue.append(
            {
                'platform': 'prodigy',
                'provider_id': pid,
                'status': status,
                'source': source,
                'metrics': _overlay_research_metrics(row),
                'metrics_label': PREAPPROVAL_METRICS_LABEL,
            }
        )
    return {'queue': queue, 'metrics_label': PREAPPROVAL_METRICS_LABEL}


_C2_ALLOWLIST_FILENAME = 'c2_paper_copy_allowlist.json'
_C2_NAMED_ID_RE = re.compile(r'^\d+$')
_C2_SNAPSHOT_NOT_TICKET_PT = (
    'Instantâneo de ordens ativas — não é ticket nem autoriza execução.'
)


def _repo_config_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_c2_allowlist_config_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for candidate in (
        Path(root) / 'config' / _C2_ALLOWLIST_FILENAME,
        _repo_config_root() / 'config' / _C2_ALLOWLIST_FILENAME,
    ):
        if candidate.is_file() and candidate not in paths:
            paths.append(candidate)
    return paths


def _parse_numeric_ids(values: Any) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    if not isinstance(values, list):
        return out
    for raw in values:
        text = str(raw).strip()
        if not _C2_NAMED_ID_RE.match(text) or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return sorted(out, key=int)


def _c2_approved_ids_from_env() -> list[str]:
    raw = os.environ.get('C2_PAPER_COPY_APPROVED_IDS', '').strip()
    if not raw:
        return []
    parts = [p.strip() for p in raw.replace(';', ',').split(',')]
    return _parse_numeric_ids(parts)


def load_c2_paper_copy_approved_ids(root: Path) -> list[str]:
    """Named Collective2 strategy IDs approved for paper-copy (default empty)."""
    merged: list[str] = []
    seen: set[str] = set()
    for path in _load_c2_allowlist_config_paths(root):
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(payload, dict):
            continue
        for item in _parse_numeric_ids(payload.get('approved_ids')):
            if item not in seen:
                seen.add(item)
                merged.append(item)
    for item in _c2_approved_ids_from_env():
        if item not in seen:
            seen.add(item)
            merged.append(item)
    return sorted(merged, key=int)


def _load_c2_research_candidates(root: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for rel in (
        'intelligence/provider-research-top10-latest.json',
        'reports/intelligence/provider-research-top10-latest.json',
    ):
        path = Path(root) / rel
        if not path.is_file():
            path = _repo_config_root() / rel
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get('mode') == 'PRODIGY_RANK_RESEARCH_ONLY':
            continue
        top = payload.get('top_10_research') or []
        for row in top:
            if not isinstance(row, dict):
                continue
            pid = row.get('provider_id') or row.get('provider')
            if pid is None:
                continue
            pid_text = str(pid).strip()
            if not pid_text:
                continue
            item = {
                'provider_id': pid_text,
                'name': row.get('name') or pid_text,
                'label': 'research_only',
                'eligible_for_copy': False,
            }
            item.update(_overlay_research_metrics(row))
            candidates.append(item)
        if candidates:
            break
    return candidates


def _load_c2_active_orders_snapshot(root: Path) -> dict[str, Any] | None:
    for rel in (
        'reports/providers/signals/active-orders-latest.json',
        'providers/signals/active-orders-latest.json',
    ):
        path = Path(root) / rel
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(payload, dict):
            continue
        return {
            'mode': payload.get('mode') or 'C2_ACTIVE_ORDERS_READ_ONLY',
            'as_of': payload.get('as_of'),
            'strategy_ids': payload.get('strategy_ids') or [],
            'active_orders_count': len(payload.get('records') or []),
            'execution_authorized': False,
            'not_a_ticket_label_pt': _C2_SNAPSHOT_NOT_TICKET_PT,
            'orders_sent': 0,
        }
    return None


def _is_collective2_order_row(row: dict[str, Any]) -> bool:
    origin = str(row.get('origin') or row.get('provider') or '').lower()
    if 'collective2' in origin or origin == 'c2':
        return True
    sk = str(row.get('strategy_key') or '').lower()
    return 'collective2' in sk or sk == 'c2'


def _collective2_operating_rows(
    open_orders: list[dict[str, Any]],
    order_history: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in (open_orders, order_history):
        for row in source:
            if not isinstance(row, dict) or not _is_collective2_order_row(row):
                continue
            key = str(row.get('client_order_id') or row.get('symbol') or '')
            if key in seen:
                continue
            seen.add(key)
            rows.append(dict(row))
    return rows


def _build_collective2_block(root: Path, approved_ids: list[str]) -> dict[str, Any]:
    subscribed = [
        {
            'provider_id': pid,
            'status': 'subscribed_named',
            'label': 'named_allowlist',
        }
        for pid in approved_ids
    ]
    return {
        'approved_ids': list(approved_ids),
        'approved_for_paper_copy': bool(approved_ids),
        'status': 'allowlist' if approved_ids else 'closed',
        'subscribed': subscribed,
        'candidates': _load_c2_research_candidates(root),
        'active_orders_snapshot': _load_c2_active_orders_snapshot(root),
    }


def _build_copy_adoption(strategy_catalog: dict[str, Any] | None) -> dict[str, Any]:
    catalog = strategy_catalog if isinstance(strategy_catalog, dict) else {}
    phases: list[dict[str, Any]] = []
    for row in catalog.get('strategies') or []:
        if not isinstance(row, dict):
            continue
        key = str(row.get('strategy_key') or '')
        if key in ('signal_copy', 'prodigy_15d'):
            phases.append(row)
    criteria_pt = [
        'Cópia de sinais de terceiros (TradingView / provedores).',
        'Prodígio: janela móvel de 15 dias, mínimo de 5 operações em pelo menos 3 dias, '
        'retorno líquido positivo, drawdown e consistência; fórmula de pontuação ainda pendente.',
        'Risco paper inicial sugerido: R$ 20; fase padrão pesquisa; ranking não promove sozinho.',
        'Fases: pesquisa, sombra, paper limitado, paper validado — promoção somente operador.',
        'Live desligado; fase não sobe por lucratividade aparente nem HTTP 200.',
        'Collective2: cópia paper só após pré-aprovação no painel; JSON/ambiente são semente se não houver decisão no livro-razão.',
        'Performance e inventário: somente fill confirmado (valores brutos se o custo faltar).',
    ]
    return {
        'criteria_pt': criteria_pt,
        'catalog_phases': phases,
        'collective2_closed': True,
        'collective2_named_allowlist': True,
        'auto_promote': False,
        'live_trading_enabled': False,
        'source': 'REQUIREMENTS Feature 4, 9 and 10',
    }


def _build_prodigy_pool(root: Path) -> dict[str, Any]:
    try:
        from trading_dashboard_data import _load_prodigy_opportunities
    except ImportError:
        return {
            'status': 'UNAVAILABLE',
            'items': [],
            'label': 'research_tip',
            'disclaimer': 'Research rank only; does not authorize orders.',
        }
    pool = _load_prodigy_opportunities(root)
    if isinstance(pool, dict):
        pool = dict(pool)
        pool.setdefault('label', 'research_tip')
    return pool


def build_panel_copy(
    root: Path,
    open_orders: list[dict[str, Any]],
    order_history: list[dict[str, Any]],
    perf: dict[str, Any] | None,
    research_copies: list[dict[str, Any]],
    *,
    strategy_catalog: dict[str, Any] | None = None,
    conn_factory: Callable[..., Any] | None = None,
    signals: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    operating = _signal_copy_rows(open_orders)
    history = _signal_copy_rows(order_history)
    approved_ids = resolve_c2_paper_copy_approved_ids(root, conn_factory)
    collective2 = _build_collective2_block(root, approved_ids)
    c2_operating = _collective2_operating_rows(open_orders, order_history)
    adoption = _build_copy_adoption(strategy_catalog)
    adoption['collective2_closed'] = not bool(approved_ids)
    preapproval = build_preapproval_queue(root, conn_factory, signals=signals)
    refresh_meta = load_candidates_refresh(root)
    copy_block: dict[str, Any] = {
        'operating': operating,
        'history': history,
        'performance': _copy_performance_slice(perf),
        'collective2': collective2,
        'collective2_operating': c2_operating,
        'research_copies': list(research_copies),
        'providers': _copy_providers(research_copies),
        'inventory': _build_copy_inventory(operating, history),
        'adoption': adoption,
        'prodigy_pool': _build_prodigy_pool(root),
        'preapproval': preapproval,
    }
    if refresh_meta:
        copy_block['candidates_refresh'] = refresh_meta
    return copy_block


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
    research_copies = prodigy_copied_signals(root)
    open_orders = load_panel_open_orders(root, conn_factory)
    order_history = load_panel_order_history(root, conn_factory)
    strategy_catalog = load_panel_strategy_catalog(conn_factory)
    signals = load_panel_signals(root, conn_factory, flags)
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'signals': signals,
        'open_orders': open_orders,
        'order_history': order_history,
        'prodigy': {
            'ranking': None,
            'copied_signals': research_copies,
            'disclaimer': 'research_only_not_order_auth',
        },
        'performance': perf,
        'copy': build_panel_copy(
            root,
            open_orders,
            order_history,
            perf,
            research_copies,
            strategy_catalog=strategy_catalog,
            conn_factory=conn_factory,
            signals=signals,
        ),
        'strategy_catalog': strategy_catalog,
        'timesfm': load_panel_timesfm(root),
        'live_trading_ui': {'enabled': False, 'control_visible': False},
    }
