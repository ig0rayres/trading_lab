"""Prodigy rank row → signed external signal for paper gateway (no phase promotion).

Rank output stays PRODIGY_RANK_RESEARCH_ONLY; this module maps provider_id + operator
ticket into signal_copy schema. Never updates strategy_states.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from gate_b_risk import broker_open_positions, evaluate_signed_signal
from paper_audit import validate_env
from paper_gateway_queue import process_after_gate_b
from signal_copy import sign, validate
from strategy_catalog import DEFAULT_PHASE_BY_KEY, gate_b_strategy_reject, normalize_strategy_key

PRODIGY_STRATEGY_KEY = 'prodigy_15d'
TICKET_REQUIRED = frozenset({'symbol', 'side', 'entry', 'stop', 'target', 'quantity'})
DEFAULT_TTL_SECONDS = 30


def _rank_mode_label() -> str:
    return 'PRODIGY_RANK_RESEARCH_ONLY'


def execution_authorized() -> bool:
    return False


def _live_guard(env: dict[str, str]) -> str | None:
    if env.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        return 'LIVE_TRADING_DISABLED_REQUIRED'
    return None


def _ticket_gap(ticket: dict[str, Any]) -> str | None:
    if not isinstance(ticket, dict):
        return 'TICKET_FIELDS_REQUIRED'
    for key in TICKET_REQUIRED:
        if ticket.get(key) in (None, ''):
            return 'TICKET_FIELDS_REQUIRED'
    return None


def _provider_from_rank(rank_row: dict[str, Any]) -> str | None:
    raw = rank_row.get('provider_id')
    if raw is None or raw == '':
        return None
    provider = str(raw).strip()
    if len(provider) < 2:
        return None
    return provider


def map_rank_to_signal(
    rank_row: dict[str, Any],
    ticket: dict[str, Any],
    secret: str,
    *,
    now: datetime | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    gap = _ticket_gap(ticket)
    if gap:
        return None, gap
    provider = _provider_from_rank(rank_row)
    if not provider:
        return None, 'RANK_PROVIDER_REQUIRED'
    now = now or datetime.now(timezone.utc)
    sid = str(ticket.get('signal_id') or f'prodigy-{provider}-{ticket["symbol"]}').strip()
    strategy_key = str(ticket.get('strategy_key') or PRODIGY_STRATEGY_KEY).strip().lower()
    body: dict[str, Any] = {
        'provider': provider,
        'signal_id': sid,
        'symbol': str(ticket['symbol']).upper(),
        'side': str(ticket.get('side') or 'buy').lower(),
        'asset_class': str(ticket.get('asset_class') or 'us_equity').lower(),
        'sent_at_utc': now.isoformat(),
        'entry': str(ticket['entry']),
        'stop': str(ticket['stop']),
        'target': str(ticket['target']),
        'quantity': int(ticket['quantity']),
        'ttl_seconds': int(ticket.get('ttl_seconds', DEFAULT_TTL_SECONDS)),
        'strategy_key': strategy_key,
    }
    body['provider_signature'] = sign(body, secret)
    return body, None


def _blocked(rank_mode: str, **fields: Any) -> dict[str, Any]:
    base = {'execution_authorized': execution_authorized(), 'rank_mode': rank_mode, 'orders_sent': 0}
    base.update(fields)
    return base


def _default_phase_override(
    signal: dict[str, Any],
    strategy_phase: str | None,
) -> str | None:
    if strategy_phase is not None:
        return strategy_phase
    if os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return None
    key = normalize_strategy_key(signal.get('strategy_key'))
    if not key:
        return None
    return DEFAULT_PHASE_BY_KEY.get(key)


def _submit_signed(
    signal: dict[str, Any],
    env: dict[str, str],
    *,
    strategy_phase: str | None,
    now: datetime | None,
    broker_get,
    process_fn: Callable | None,
    conn_factory,
) -> dict[str, Any]:
    secret = env.get('SIGNAL_COPY_SECRET', '')
    try:
        fx = validate_env(env)
    except (KeyError, ValueError, TypeError) as exc:
        code = type(exc).__name__
        return _blocked(_rank_mode_label(), status='BLOCKED', reject_code=code, reasons=[code], signal=signal)
    errs = validate(signal, secret, fx, now=now)
    if errs:
        return _blocked(_rank_mode_label(), status='BLOCKED', reasons=errs, signal=signal)
    open_pos = broker_open_positions(broker_get, env) if broker_get else None
    decision = evaluate_signed_signal(
        signal, fx=fx, env=env, open_positions=open_pos,
        strategy_phase=strategy_phase, conn_factory=conn_factory, now=now,
    )
    runner = process_fn or process_after_gate_b
    result = dict(runner(signal, decision, env, conn_factory=conn_factory))
    result.setdefault('execution_authorized', execution_authorized())
    result.setdefault('rank_mode', _rank_mode_label())
    result['signal'] = signal
    return result


def ingest(
    rank_row: dict[str, Any],
    ticket: dict[str, Any],
    env: dict[str, str],
    *,
    strategy_phase: str | None = None,
    dry_run: bool = True,
    now: datetime | None = None,
    broker_get=None,
    process_fn: Callable | None = None,
    conn_factory=None,
) -> dict[str, Any]:
    live_code = _live_guard(env)
    rank_mode = _rank_mode_label()
    if live_code:
        return _blocked(rank_mode, status='BLOCKED', reject_code=live_code, reasons=[live_code])
    secret = env.get('SIGNAL_COPY_SECRET', '')
    signal, map_err = map_rank_to_signal(rank_row, ticket, secret, now=now)
    if map_err:
        return _blocked(rank_mode, status='BLOCKED', reject_code=map_err, reasons=[map_err])
    assert signal is not None
    phase = _default_phase_override(signal, strategy_phase)
    strat_code = gate_b_strategy_reject(signal, strategy_phase=phase, conn_factory=conn_factory)
    if strat_code:
        return _blocked(
            rank_mode, status='BLOCKED', reject_code=strat_code, reasons=[strat_code], signal=signal,
        )
    if dry_run:
        return {'status': 'DRY_RUN', 'signal': signal, 'orders_sent': 0,
                'execution_authorized': execution_authorized(), 'rank_mode': rank_mode}
    return _submit_signed(
        signal, env, strategy_phase=phase, now=now, broker_get=broker_get,
        process_fn=process_fn, conn_factory=conn_factory,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description='Prodigy rank row → signed signal (dry-run default)')
    parser.add_argument('--rank-row', required=True, help='JSON file: one provider row from prodigy-rank')
    parser.add_argument('--ticket', required=True, help='JSON file: operator ticket fields')
    parser.add_argument('--submit', action='store_true', help='Run Gate B + paper queue (still no live trading)')
    args = parser.parse_args()
    env = dict(os.environ)
    live_code = _live_guard(env)
    if live_code:
        print(json.dumps({'status': 'BLOCKED', 'reject_code': live_code, 'orders_sent': 0}, indent=2))
        return 2
    try:
        rank_row = json.loads(Path(args.rank_row).read_text())
        ticket = json.loads(Path(args.ticket).read_text())
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reasons': [type(exc).__name__], 'orders_sent': 0}, indent=2))
        return 2
    from paper_audit import get_json

    result = ingest(
        rank_row, ticket, env, dry_run=not args.submit, broker_get=get_json,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    ok = result.get('status') in ('DRY_RUN', 'QUEUED', 'PAPER_SUBMITTED', 'PREVIEW_ONLY')
    if result.get('status') == 'BLOCKED' and result.get('reject_code') == 'STRATEGY_PHASE_BLOCKED':
        return 0
    return 0 if ok or result.get('orders_sent') == 0 else 2


if __name__ == '__main__':
    raise SystemExit(main())