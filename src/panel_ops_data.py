"""Operational panel data: signals, performance, blocked-signal context. No broker calls."""
from __future__ import annotations

import json
import math
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
    if history:
        row['realized_gross_pnl_usd'] = snap.get('realized_gross_pnl_usd')
        row['pnl_label'] = PERFORMANCE_LABEL_GROSS
        row['broker_fill_confirmed'] = snap.get('broker_fill_confirmed')
    return _sanitize_order_row(row)


def open_orders_from_snapshots(root: Path) -> list[dict[str, Any]]:
    rows = [
        order_row_from_snapshot(snap)
        for snap in latest_monitored_snapshots(root).values()
        if snapshot_is_open_order(snap)
    ]
    return sorted(rows, key=lambda item: str(item.get('symbol') or ''))


def order_history_from_snapshots(root: Path) -> list[dict[str, Any]]:
    rows = [
        order_row_from_snapshot(snap, history=True)
        for snap in latest_monitored_snapshots(root).values()
        if snapshot_is_confirmed_fill(snap)
    ]
    return sorted(rows, key=lambda item: str(item.get('symbol') or ''))


def _ledger_open_order_row(
    cid: Any,
    symbol: Any,
    side: Any,
    status: Any,
    qty: Any,
    broker_id: Any,
    strategy_key: Any,
) -> dict[str, Any]:
    return _sanitize_order_row({
        'client_order_id': cid,
        'symbol': symbol,
        'side': side,
        'status': status,
        'entry_qty': qty,
        'remaining_qty': qty,
        'broker_order_id': broker_id,
        'strategy_key': strategy_key,
        'market': 'US_EQUITY',
    })


def open_orders_from_ledger(conn_factory: Callable[..., Any]) -> list[dict[str, Any]] | None:
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT po.client_order_id, po.symbol, po.side, po.status, po.qty, '
                    'po.broker_order_id, rd.strategy_key '
                    'FROM paper_orders po '
                    'JOIN risk_decisions rd ON rd.id = po.risk_decision_id AND rd.deleted_at IS NULL '
                    'WHERE po.deleted_at IS NULL AND po.status != %s '
                    'ORDER BY po.created_at DESC LIMIT 100',
                    ('filled',),
                )
                fetched = cur.fetchall()
        if not fetched:
            return None
        rows = [
            _ledger_open_order_row(cid, symbol, side, status, qty, broker_id, strategy_key)
            for cid, symbol, side, status, qty, broker_id, strategy_key in fetched
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
) -> dict[str, Any] | None:
    if str(status) in EXCLUDED_PNL_ORDER_STATUSES:
        return None
    gross = None
    if cents is not None:
        gross = str(Decimal(cents) / Decimal(100))
    return _sanitize_order_row({
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
    })


def order_history_from_ledger(conn_factory: Callable[..., Any]) -> list[dict[str, Any]] | None:
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT po.client_order_id, po.symbol, po.side, po.status, po.broker_order_id, '
                    'rd.strategy_key, pf.qty, le.amount_cents, pf.filled_at '
                    'FROM paper_fills pf '
                    'JOIN paper_orders po ON po.id = pf.paper_order_id AND po.deleted_at IS NULL '
                    'JOIN risk_decisions rd ON rd.id = po.risk_decision_id AND rd.deleted_at IS NULL '
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
    if conn_factory is not None:
        try:
            from_db = open_orders_from_ledger(conn_factory)
            if from_db:
                return from_db
        except Exception:
            pass
    try:
        return open_orders_from_snapshots(root)
    except Exception:
        return []


def load_panel_order_history(root: Path, conn_factory: Callable[..., Any] | None) -> list[dict[str, Any]]:
    if conn_factory is not None:
        try:
            from_db = order_history_from_ledger(conn_factory)
            if from_db:
                return from_db
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


def build_panel_copy(
    open_orders: list[dict[str, Any]],
    order_history: list[dict[str, Any]],
    perf: dict[str, Any] | None,
    research_copies: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        'operating': _signal_copy_rows(open_orders),
        'history': _signal_copy_rows(order_history),
        'performance': _copy_performance_slice(perf),
        'collective2': {'approved_for_paper_copy': False, 'status': 'closed'},
        'research_copies': list(research_copies),
        'providers': _copy_providers(research_copies),
    }


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
    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'signals': load_panel_signals(root, conn_factory, flags),
        'open_orders': open_orders,
        'order_history': order_history,
        'prodigy': {
            'ranking': None,
            'copied_signals': research_copies,
            'disclaimer': 'research_only_not_order_auth',
        },
        'performance': perf,
        'copy': build_panel_copy(open_orders, order_history, perf, research_copies),
        'strategy_catalog': load_panel_strategy_catalog(conn_factory),
        'timesfm': load_panel_timesfm(root),
        'live_trading_ui': {'enabled': False, 'control_visible': False},
    }
