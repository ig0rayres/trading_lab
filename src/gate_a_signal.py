"""Gate A: persist authenticated signals to signal_events. No broker calls."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


def idempotency_key(provider: str, signal_id: str) -> str:
    return hashlib.sha256((provider + '|' + signal_id).encode()).hexdigest()


def record_signal_event(
    conn,
    *,
    payload: dict[str, Any],
    http_status: int,
    body: dict[str, Any],
    received_at: datetime | None = None,
) -> None:
    """Append signal_events row for audit. Rejected and queued events both recorded."""
    when = received_at or datetime.now(timezone.utc)
    if body.get('status') == 'DUPLICATE_IGNORED':
        return
    status = 'rejected' if http_status >= 400 or body.get('status') == 'REJECTED' else 'received'
    if http_status == 202 and body.get('status') == 'QUEUED':
        status = 'accepted'
    side = 'long' if payload.get('side') == 'buy' else 'short'
    reject_code = body.get('reason') if status == 'rejected' else None
    key = idempotency_key(str(payload.get('provider', '')), str(payload.get('signal_id', '')))
    if not payload.get('signal_id'):
        key = idempotency_key('unknown', body.get('reference', 'reject'))
    row = {
        'idempotency_key': key,
        'source': str(payload.get('provider', 'tradingview')),
        'symbol': str(payload.get('symbol', 'UNKNOWN'))[:32],
        'side': side,
        'status': status,
        'reject_code': reject_code,
        'received_at': when,
    }
    from ledger_store import insert_row

    insert_row(conn, 'signal_events', row)


def maybe_persist(payload, http_status, body, conn_factory=None):
    """No-op without LEDGER_DATABASE_URL. Never raises into HTTP handler."""
    import os

    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    try:
        with conn_factory() as conn:
            record_signal_event(conn, payload=payload, http_status=http_status, body=body)
            conn.commit()
    except Exception:
        return
