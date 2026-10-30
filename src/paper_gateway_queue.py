"""Paper gateway queue after Gate A+B. HTTP 200 / QUEUED is not a fill."""
from __future__ import annotations

import os
from typing import Any

from gate_a_signal import idempotency_key
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


def persist_intent(signal: dict[str, Any], decision: dict[str, Any], queue_result: dict[str, Any], conn_factory=None):
    if decision.get('decision') != 'paper_allowed':
        return
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    provider = str(signal.get('provider', 'tradingview'))
    sid = str(signal.get('signal_id', ''))
    key = idempotency_key(provider, sid) if sid else idempotency_key('unknown', queue_result['client_order_id'])
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT id FROM signal_events WHERE idempotency_key = %s AND deleted_at IS NULL',
                    (key,),
                )
                sig_row = cur.fetchone()
            if not sig_row:
                return
            signal_event_id = sig_row[0]
            from ledger_store import insert_row
            import uuid

            risk_id = uuid.uuid4()
            insert_row(
                conn,
                'risk_decisions',
                {
                    'id': risk_id,
                    'signal_event_id': signal_event_id,
                    'strategy_key': 'signal_copy',
                    'decision': 'paper_allowed',
                    'reject_code': None,
                    'risk_amount_cents': decision.get('risk_amount_cents', 0),
                },
            )
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


def process_after_gate_b(
    signal: dict[str, Any],
    decision: dict[str, Any],
    env: dict[str, str],
    *,
    ledger: str | None = None,
    broker_run=paper_run,
    conn_factory=None,
) -> dict[str, Any]:
    if decision.get('decision') != 'paper_allowed':
        code = decision.get('reject_code') or 'RISK_BLOCK'
        return {'status': 'BLOCKED', 'reasons': [code], 'orders_sent': 0}
    queued = queue_intent(signal, decision)
    persist_intent(signal, decision, queued, conn_factory=conn_factory)
    if not broker_auto_allowed(env):
        return queued
    return broker_run(signal, env, ledger or '/app/reports/paper/signal-orders.jsonl')
