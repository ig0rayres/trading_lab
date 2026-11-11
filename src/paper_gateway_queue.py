"""Paper gateway queue after Gate A+B. HTTP 200 / QUEUED is not a fill."""
from __future__ import annotations

import os
import uuid
from typing import Any

from gate_a_signal import idempotency_key
from ledger_store import insert_row
from paper_fill_cycle import track_once as default_track_once
from signal_paper_runner import make_order, run as paper_run, token


def broker_auto_allowed(env: dict[str, str]) -> bool:
    return (
        env.get('PAPER_SIGNAL_AUTO_ENABLED', 'false').lower() == 'true'
        and env.get('PAPER_EXECUTION_ENABLED', 'false').lower() == 'true'
        and env.get('PAPER_SIGNAL_ACCOUNT_ACK', '') == 'I_AUTHORIZE_ALPACA_PAPER_ONLY'
    )


def queue_intent(signal: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    fp = token(signal)
    body = make_order(signal, fp)
    return {
        'status': 'QUEUED',
        'mode': 'PAPER_GATEWAY_QUEUE_ONLY',
        'client_order_id': 'nf-' + fp,
        'order_preview': body,
        'orders_sent': 0,
        'gate_b': decision.get('decision'),
    }


def _lookup_signal_event_id(
    conn,
    signal: dict[str, Any],
    fallback_key: str | None = None,
    *,
    queue_idempotency_key: str | None = None,
):
    """Resolve Gate A row. Queue JSON uses hashed signal_id; file stem matches Gate A key."""
    keys: list[str] = []

    def add(key: str | None) -> None:
        if key and key not in keys:
            keys.append(key)

    add(queue_idempotency_key)
    provider = str(signal.get('provider', 'tradingview'))
    sid = str(signal.get('signal_id', ''))
    if sid:
        add(idempotency_key(provider, sid))
    add(fallback_key)
    if not keys:
        return None
    with conn.cursor() as cur:
        for key in keys:
            cur.execute(
                'SELECT id FROM signal_events WHERE idempotency_key = %s AND deleted_at IS NULL',
                (key,),
            )
            row = cur.fetchone()
            if row:
                return row[0]
    return None


def persist_risk_decision(
    signal: dict[str, Any],
    decision: dict[str, Any],
    *,
    queue_result: dict[str, Any] | None = None,
    queue_idempotency_key: str | None = None,
    conn_factory=None,
):
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    allowed = decision.get('decision') == 'paper_allowed'
    fallback = None
    if queue_result:
        fallback = idempotency_key('unknown', queue_result.get('client_order_id', 'reject'))
    try:
        with conn_factory() as conn:
            signal_event_id = _lookup_signal_event_id(
                conn,
                signal,
                fallback,
                queue_idempotency_key=queue_idempotency_key,
            )
            if not signal_event_id:
                return
            risk_id = uuid.uuid4()
            sk = signal.get('strategy_key') or 'signal_copy'
            insert_row(
                conn,
                'risk_decisions',
                {
                    'id': risk_id,
                    'signal_event_id': signal_event_id,
                    'strategy_key': str(sk)[:64],
                    'decision': 'paper_allowed' if allowed else 'rejected',
                    'reject_code': decision.get('reject_code'),
                    'risk_amount_cents': decision.get('risk_amount_cents', 0),
                },
            )
            if allowed and queue_result:
                insert_row(
                    conn,
                    'paper_orders',
                    {
                        'risk_decision_id': risk_id,
                        'position_id': None,
                        'client_order_id': queue_result['client_order_id'],
                        'broker_order_id': None,
                        'symbol': str(signal.get('symbol', '')).upper()[:32],
                        'side': 'long',
                        'status': 'queued_intent',
                        'qty': signal.get('quantity', 0),
                    },
                )
            conn.commit()
    except Exception:
        return


def persist_intent(
    signal: dict[str, Any],
    decision: dict[str, Any],
    queue_result: dict[str, Any],
    conn_factory=None,
    *,
    queue_idempotency_key: str | None = None,
):
    persist_risk_decision(
        signal,
        decision,
        queue_result=queue_result,
        queue_idempotency_key=queue_idempotency_key,
        conn_factory=conn_factory,
    )


def _persist_broker_submitted(
    client_order_id: str,
    broker_id: str,
    *,
    conn_factory=None,
) -> None:
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return
    if not broker_id or not client_order_id:
        return
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE paper_orders SET broker_order_id = %s, status = %s '
                    'WHERE client_order_id = %s',
                    (broker_id, 'submitted', client_order_id),
                )
            conn.commit()
    except Exception:
        return


def _load_paper_order(client_order_id: str, conn_factory=None) -> dict[str, Any] | None:
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return None
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT client_order_id, broker_order_id, symbol, side, status, qty '
                    'FROM paper_orders WHERE client_order_id = %s AND deleted_at IS NULL',
                    (client_order_id,),
                )
                row = cur.fetchone()
        if not row:
            return None
        return {
            'client_order_id': row[0],
            'broker_order_id': row[1],
            'symbol': row[2],
            'side': row[3],
            'status': row[4],
            'qty': row[5],
            'market': 'us_equity',
        }
    except Exception:
        return None


def _resume_track_existing(
    order: dict[str, Any],
    env: dict[str, str],
    *,
    track_fn=None,
) -> dict[str, Any]:
    track = track_fn or default_track_once
    out = dict(track(order, env))
    out['mode'] = 'RESUMED_AFTER_RESTART'
    out['orders_sent'] = 0
    return out


def _broker_submitted_persistable(result: dict[str, Any]) -> bool:
    if result.get('status') != 'PAPER_SUBMITTED':
        return False
    if result.get('orders_sent') != 1:
        return False
    broker_id = result.get('broker_id')
    if not broker_id:
        return False
    return bool(result.get('client_order_id'))


def process_after_gate_b(
    signal: dict[str, Any],
    decision: dict[str, Any],
    env: dict[str, str],
    *,
    ledger: str | None = None,
    broker_run=paper_run,
    track_fn=None,
    conn_factory=None,
    queue_idempotency_key: str | None = None,
) -> dict[str, Any]:
    if decision.get('decision') != 'paper_allowed':
        persist_risk_decision(
            signal,
            decision,
            conn_factory=conn_factory,
            queue_idempotency_key=queue_idempotency_key,
        )
        code = decision.get('reject_code') or 'RISK_BLOCK'
        return {'status': 'BLOCKED', 'reasons': [code], 'orders_sent': 0}
    queued = queue_intent(signal, decision)
    existing = _load_paper_order(queued['client_order_id'], conn_factory=conn_factory)
    if not existing:
        persist_intent(
            signal,
            decision,
            queued,
            conn_factory=conn_factory,
            queue_idempotency_key=queue_idempotency_key,
        )
    elif str(existing.get('broker_order_id') or '').strip():
        return _resume_track_existing(existing, env, track_fn=track_fn)
    if not broker_auto_allowed(env):
        return queued
    result = broker_run(signal, env, ledger or '/app/reports/paper/signal-orders.jsonl')
    if _broker_submitted_persistable(result):
        _persist_broker_submitted(
            str(result['client_order_id']),
            str(result['broker_id']),
            conn_factory=conn_factory,
        )
    return result
