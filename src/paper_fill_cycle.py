"""Track a submitted paper order to terminal state (ADR-007). Never authorizes live orders."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.request import Request, urlopen

from paper_audit import PAPER_URL, validate_env
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


def _default_order_timeout(env: dict[str, Any]) -> int:
    raw = env.get('PAPER_ORDER_TIMEOUT_SEC', env.get('PAPER_ORDER_TTL_SEC', '300'))
    try:
        ttl = int(raw)
    except (TypeError, ValueError):
        ttl = 300
    return max(1, ttl)


def cancel_alpaca_order(broker_order_id: str, env: dict[str, Any], opener=urlopen) -> dict[str, Any]:
    _live_forbidden(env)
    validate_env(env)
    path = '/v2/orders/' + broker_order_id
    req = Request(
        PAPER_URL + path,
        method='DELETE',
        headers={
            'APCA-API-KEY-ID': env['ALPACA_API_KEY'],
            'APCA-API-SECRET-KEY': env['ALPACA_SECRET_KEY'],
        },
    )
    with opener(req, timeout=15) as response:
        raw = response.read().decode()
        body = json.loads(raw) if raw.strip() else {}
    return {'status': 'CANCEL_ACCEPTED', 'broker_status': body.get('status'), 'orders_sent': 0}


def _record_cancelled(client_order_id: str, *, conn_factory=None) -> None:
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE paper_orders SET status = %s, updated_at = now() '
                    'WHERE client_order_id = %s AND deleted_at IS NULL',
                    ('cancelled_ttl', client_order_id),
                )
            conn.commit()
    except Exception:
        return


def track_once_with_cancel(
    order: dict[str, Any],
    env: dict[str, Any],
    **kwargs,
) -> dict[str, Any]:
    cancel = kwargs.pop('cancel_fn', None) or (
        lambda bid, e: cancel_alpaca_order(bid, e)
    )

    def _cancel_and_record(broker_id: str, e: dict[str, Any]) -> dict[str, Any]:
        out = cancel(broker_id, e)
        _record_cancelled(str(order.get('client_order_id', '')))
        return out

    out = track_once(order, env, cancel_fn=_cancel_and_record, **kwargs)
    return out


def list_open_paper_orders(conn_factory=None) -> list[dict[str, Any]]:
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return []
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    rows: list[dict[str, Any]] = []
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT client_order_id, broker_order_id, symbol, side, status, qty, '
                    'created_at, updated_at, market '
                    'FROM paper_orders '
                    'WHERE deleted_at IS NULL AND broker_order_id IS NOT NULL '
                    "AND status IN ('submitted', 'accepted', 'new', 'queued_intent')",
                )
                for row in cur.fetchall():
                    rows.append({
                        'client_order_id': row[0],
                        'broker_order_id': row[1],
                        'symbol': row[2],
                        'side': row[3],
                        'status': row[4],
                        'qty': row[5],
                        'created_at': row[6],
                        'updated_at': row[7],
                        'market': row[8] or 'us_equity',
                    })
    except Exception:
        return []
    return rows


def _enrich_order(order: dict[str, Any], env: dict[str, Any]) -> dict[str, Any]:
    out = dict(order)
    submitted = order.get('updated_at') or order.get('created_at')
    if submitted is not None and hasattr(submitted, 'isoformat'):
        submitted = submitted.astimezone(timezone.utc).isoformat()
    out['submitted_at_utc'] = str(submitted or '')
    out['ttl_seconds'] = int(order.get('ttl_seconds') or _default_order_timeout(env))
    return out


def track_open_once(env: dict[str, Any], *, conn_factory=None) -> dict[str, Any]:
    orders = list_open_paper_orders(conn_factory=conn_factory)
    outcomes = []
    for raw in orders:
        enriched = _enrich_order(raw, env)
        outcomes.append(track_once_with_cancel(enriched, env))
    return {'status': 'TRACKED_BATCH', 'count': len(outcomes), 'outcomes': outcomes, 'orders_sent': 0}


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


def main() -> None:
    parser = argparse.ArgumentParser(description='Track open paper orders; cancel on TTL expiry')
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args()
    if not args.once:
        parser.error('--once required')
    result = track_open_once(os.environ)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
