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
    if body.get('status') == 'received':
        status = 'received'
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


def persist_news_first_report(report, conn_factory=None):
    """Append one signal_events row per News First review signal (NO_TRADE audit)."""
    if report.get('mode') != 'NEWS_FIRST_INTERNAL_SIMULATION':
        return 0
    count = 0
    for sig in report.get('signals', []):
        sid = str(sig.get('id', '')).strip()
        sym = str(sig.get('symbol', 'UNKNOWN')).upper()[:32]
        if not sid or not sym:
            continue
        payload = {
            'provider': 'news_first',
            'signal_id': sid,
            'symbol': sym,
            'side': 'buy',
        }
        reason = 'EVIDENCE_PENDING'
        if sig.get('decision') != 'NO_TRADE' and sig.get('blocker_reasons'):
            reason = str(sig['blocker_reasons'][0])[:64]
        body = {'status': 'REJECTED', 'reason': reason, 'orders_sent': 0}
        maybe_persist(payload, 422, body, conn_factory=conn_factory)
        count += 1
    return count


def persist_signal_copy_preflight(signal, result, conn_factory=None):
    """Audit signed copy preflight; never places orders."""
    if not isinstance(signal, dict):
        return
    payload = {
        'provider': str(signal.get('provider', 'signal_copy')),
        'signal_id': str(signal.get('signal_id', '')),
        'symbol': str(signal.get('symbol', 'UNKNOWN')),
        'side': signal.get('side', 'buy'),
    }
    if not payload['signal_id']:
        return
    if result.get('status') == 'BLOCKED':
        reasons = result.get('reasons') or ['BLOCKED']
        body = {'status': 'REJECTED', 'reason': str(reasons[0])[:64], 'orders_sent': 0}
        maybe_persist(payload, 422, body, conn_factory=conn_factory)
    elif result.get('status') == 'SIGNAL_ACCEPTED_RISK_PREVIEW':
        maybe_persist(payload, 200, {'status': 'received', 'orders_sent': 0}, conn_factory=conn_factory)
