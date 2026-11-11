"""Track a submitted paper order to terminal state (ADR-007). Never authorizes live orders."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from paper_audit import validate_env
from paper_reconcile import reconcile as default_reconcile

_TERMINAL = frozenset({'filled', 'canceled', 'expired', 'rejected', 'done_for_day'})


def _parse_utc(value: str) -> datetime:
    text = value.replace('Z', '+00:00')
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _ttl_expired(order: dict[str, Any], now_utc: str) -> bool:
    submitted = order.get('submitted_at_utc')
    ttl = order.get('ttl_seconds')
    if not submitted or ttl is None:
        return False
    try:
        elapsed = (_parse_utc(now_utc) - _parse_utc(str(submitted))).total_seconds()
        return elapsed > int(ttl)
    except (TypeError, ValueError):
        return False


def _broker_status(report: dict[str, Any]) -> str:
    return str(report.get('broker_status') or '').lower()


def _is_terminal_report(report: dict[str, Any]) -> bool:
    if 'terminal' in report:
        return bool(report['terminal'])
    return _broker_status(report) in _TERMINAL


def _is_shadow_path(order: dict[str, Any], report: dict[str, Any]) -> bool:
    if str(order.get('broker_source', '')).lower() == 'shadow':
        return True
    return report.get('source') == 'LOCAL_SHADOW_BROKER'


def _live_forbidden(env: dict[str, Any]) -> None:
    if str(env.get('LIVE_TRADING_ENABLED', 'false')).lower() not in ('false', '0', 'no'):
        raise ValueError('LIVE_TRADING_FORBIDDEN')


def _ledger_report(report: dict[str, Any], order: dict[str, Any]) -> dict[str, Any]:
    fill_id = report.get('id') or report.get('broker_order_id') or order.get('broker_order_id')
    side = report.get('side') or ('buy' if order.get('side') == 'long' else order.get('side'))
    return {
        'mode': 'READ_ONLY',
        'activities': {
            'activities': [{
                'id': str(fill_id),
                'symbol': report.get('symbol') or order.get('symbol'),
                'side': side,
                'qty': report.get('filled_qty') or order.get('qty'),
                'price': report.get('filled_avg_price'),
            }],
        },
    }


def _tracked_status(report: dict[str, Any], order: dict[str, Any]) -> str:
    status = _broker_status(report)
    if status == 'filled' and _is_shadow_path(order, report):
        return 'TRACKED_SHADOW_NO_FILL'
    if status == 'filled':
        return 'TRACKED_FILLED'
    if status == 'canceled':
        return 'TRACKED_CANCELED'
    if status == 'expired':
        return 'TRACKED_EXPIRED'
    return 'TRACKED_' + status.upper() if status else 'RECONCILED'


def _treated_as_fill(report: dict[str, Any], order: dict[str, Any]) -> bool:
    if report.get('treated_as_fill') is False:
        return False
    if _is_shadow_path(order, report):
        return False
    return _broker_status(report) == 'filled'


def may_auto_resubmit(order: dict[str, Any], env: dict[str, Any]) -> bool:
    _live_forbidden(env)
    if order.get('idempotency_key'):
        return False
    return False


def track_once(
    order: dict[str, Any],
    env: dict[str, Any],
    *,
    now_utc: str | None = None,
    reconcile_fn: Callable[..., dict[str, Any]] | None = None,
    ledger_apply_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    cancel_fn: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    _live_forbidden(env)
    validate_env(env)
    reconcile = reconcile_fn or default_reconcile
    cid = str(order['client_order_id'])
    report = reconcile(cid, env)
    if report.get('status') != 'RECONCILED':
        out = dict(report)
        out.setdefault('orders_sent', 0)
        out.setdefault('terminal', False)
        out.setdefault('treated_as_fill', False)
        return out

    now_s = now_utc or datetime.now(timezone.utc).isoformat()
    if not _is_terminal_report(report) and _ttl_expired(order, now_s):
        broker_id = str(order.get('broker_order_id') or '')
        if cancel_fn and broker_id:
            cancel_fn(broker_id, env)
        return {
            'status': 'TRACKED_CANCELLED_TTL',
            'orders_sent': 0,
            'terminal': True,
            'treated_as_fill': False,
            'client_order_id': cid,
        }

    treated = _treated_as_fill(report, order)
    track_status = _tracked_status(report, order)
    out: dict[str, Any] = {
        'status': track_status,
        'orders_sent': 0,
        'terminal': _is_terminal_report(report) or track_status.endswith('_TTL'),
        'treated_as_fill': treated,
        'client_order_id': cid,
    }
    if treated and ledger_apply_fn is not None:
        ledger_apply_fn(_ledger_report(report, order))
    return out
