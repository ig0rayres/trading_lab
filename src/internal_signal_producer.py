"""Signed internal strategy signals into the TradingView queue path. No broker calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from gate_a_signal import idempotency_key, maybe_persist
from gate_b_risk import config_for_fx
from paper_audit import amount
from risk_control_flags import fetch_control_flags
from signal_copy import DEFAULT_MAX_AGE, sign, validate

PROVIDER_BY_STRATEGY = {
    'momentum': 'lab_momentum',
    'ta_barato': 'lab_ta_barato',
}

_QUEUE = Path(os.environ.get('TV_QUEUE_DIR', '/app/reports/webhooks/pending'))
_SIGNAL_ID_RE = re.compile(r'^[a-zA-Z0-9_-]{6,100}$')


def provider_for_strategy(strategy_key: str) -> str | None:
    return PROVIDER_BY_STRATEGY.get(str(strategy_key or '').strip().lower())


def deterministic_signal_id(strategy_key: str, symbol: str, bar_date: str) -> str:
    raw = f'{strategy_key}|{symbol.upper()}|{bar_date}'
    digest = hashlib.sha256(raw.encode()).hexdigest()[:48]
    return f'{strategy_key}_{digest}'


def _merge_budget_cfg(fx: Decimal, flags: dict[str, Any] | None, *, fractional: bool) -> dict[str, Any]:
    cfg = config_for_fx(fx, flags)
    cfg.update(
        {
            'allow_margin': False,
            'allow_short': False,
            'allow_options': False,
            'max_position_pct': 75,
            'cash_buffer_pct': 10,
            'min_reward_risk': 1.0,
            'fractional': fractional,
        }
    )
    return cfg


def _fractional_qty_from_limits(sized: dict[str, Any]) -> Decimal | None:
    limits = sized.get('limits') or []
    caps: list[Decimal] = []
    for lim in limits:
        per = amount(lim.get('per'))
        usd = amount(lim.get('usd'))
        if per > 0:
            caps.append(usd / per)
    if not caps:
        return None
    qty = min(caps)
    if qty <= 0:
        return None
    return qty


def _format_crypto_qty(qty: Decimal) -> str:
    text = format(qty.normalize(), 'f')
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    return text or '0'


def _resolve_quantity(sized: dict[str, Any], *, fractional: bool) -> int | str | None:
    whole = int(sized.get('qty') or 0)
    if whole >= 1:
        return whole
    if fractional:
        frac = _fractional_qty_from_limits(sized)
        if frac is not None and frac > 0:
            return _format_crypto_qty(frac)
    if sized.get('refusal'):
        return None
    return None


def plan_levels_from_close(
    orig: Any,
    *,
    symbol: str,
    entry_price: float,
    bar_date: str,
    fx: Decimal,
    flags: dict[str, Any] | None = None,
    asset_class: str = 'us_equity',
) -> dict[str, Any] | None:
    """Stop/target/qty via upstream exit + budget only."""
    fractional = str(asset_class or '').lower() == 'crypto'
    sr, sp = orig.exit.parse_stop('pct:1')
    tr, tp = orig.exit.parse_target('1R')
    plan = orig.exit.compute(entry_price, sr, sp, tr, tp)
    doc = {
        'symbol': symbol.upper(),
        'side': 'buy',
        'date': bar_date,
        'setup': 'level',
        'entry': str(plan['entry']),
        'stop': str(plan['stop']),
        'target': str(plan['target']),
    }
    sized = orig.budget.size_trade(
        doc, _merge_budget_cfg(fx, flags, fractional=fractional), today=bar_date
    )
    qty = _resolve_quantity(sized, fractional=fractional)
    if qty is None:
        return None
    return {
        'entry': str(plan['entry']),
        'stop': str(plan['stop']),
        'target': str(plan['target']),
        'quantity': qty,
    }


def build_signed_signal(
    *,
    strategy_key: str,
    symbol: str,
    asset_class: str,
    bar_date: str,
    levels: dict[str, Any],
    secret: str,
    now: datetime | None = None,
    ttl_seconds: int | None = None,
) -> dict[str, Any] | None:
    provider = provider_for_strategy(strategy_key)
    if not provider or len(secret) < 24:
        return None
    sid = deterministic_signal_id(strategy_key, symbol, bar_date)
    if not _SIGNAL_ID_RE.fullmatch(sid):
        return None
    when = now or datetime.now(timezone.utc)
    ttl = int(ttl_seconds if ttl_seconds is not None else DEFAULT_MAX_AGE)
    body: dict[str, Any] = {
        'provider': provider,
        'signal_id': sid,
        'symbol': symbol.upper(),
        'side': 'buy',
        'asset_class': asset_class,
        'sent_at_utc': when.isoformat(),
        'entry': levels['entry'],
        'stop': levels['stop'],
        'target': levels['target'],
        'quantity': levels['quantity'],
        'ttl_seconds': ttl,
        'strategy_key': strategy_key,
    }
    body['provider_signature'] = sign(body, secret)
    return body


def _queue_paths(queue: Path, signal: dict[str, Any]) -> tuple[Path, Path]:
    digest = idempotency_key(str(signal['provider']), str(signal['signal_id']))
    pending = queue / f'{digest}.json'
    processed = queue.parent / 'processed' / pending.name
    return pending, processed


def _persist_queue_file(q: Path, signal: dict[str, Any]) -> dict[str, Any]:
    pending, processed = _queue_paths(q, signal)
    if pending.exists() or processed.exists():
        body = {'status': 'DUPLICATE_IGNORED', 'orders_sent': 0}
        maybe_persist(signal, 200, body)
        return body
    with tempfile.NamedTemporaryFile('w', dir=q, delete=False, prefix='.tmp-', encoding='utf-8') as f:
        json.dump(signal, f, separators=(',', ':'))
        tmp = Path(f.name)
    try:
        os.link(tmp, pending)
    except FileExistsError:
        tmp.unlink(missing_ok=True)
        body = {'status': 'DUPLICATE_IGNORED', 'orders_sent': 0}
        maybe_persist(signal, 200, body)
        return body
    finally:
        tmp.unlink(missing_ok=True)
    body = {'status': 'QUEUED', 'reference': pending.stem[:16], 'orders_sent': 0}
    maybe_persist(signal, 202, body)
    return body


def enqueue_signed_signal(
    signal: dict[str, Any],
    *,
    queue: Path | None = None,
    now: datetime | None = None,
    secret: str | None = None,
) -> dict[str, Any]:
    """Persist Gate A audit and write pending queue file (idempotent)."""
    if os.environ.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        return {'status': 'BLOCKED', 'reason': 'LIVE_FORBIDDEN', 'orders_sent': 0}
    if not signal.get('strategy_key'):
        return {'status': 'BLOCKED', 'reason': 'STRATEGY_KEY_REQUIRED', 'orders_sent': 0}
    sec = secret if secret is not None else os.environ.get('SIGNAL_COPY_SECRET', '')
    fx = amount(os.environ.get('USD_BRL_REFERENCE', '5'))
    when = now or datetime.now(timezone.utc)
    errs = validate(signal, sec, fx, now=when)
    if errs:
        body = {'status': 'REJECTED', 'reason': str(errs[0]), 'orders_sent': 0}
        maybe_persist(signal, 422, body)
        return {'status': 'BLOCKED', 'reasons': errs, 'orders_sent': 0}
    q = queue or _QUEUE
    q.mkdir(parents=True, exist_ok=True)
    return _persist_queue_file(q, signal)


def emit_internal_signal(
    *,
    strategy_key: str,
    symbol: str,
    asset_class: str,
    bar_date: str,
    levels: dict[str, Any],
    queue: Path | None = None,
    now: datetime | None = None,
    secret: str | None = None,
) -> dict[str, Any]:
    sec = secret if secret is not None else os.environ.get('SIGNAL_COPY_SECRET', '')
    signed = build_signed_signal(
        strategy_key=strategy_key,
        symbol=symbol,
        asset_class=asset_class,
        bar_date=bar_date,
        levels=levels,
        secret=sec,
        now=now,
    )
    if signed is None:
        return {'status': 'BLOCKED', 'reason': 'BUILD_FAILED', 'orders_sent': 0}
    return enqueue_signed_signal(signed, queue=queue, now=now, secret=sec)


def main(argv: list[str] | None = None) -> int:
    raise SystemExit('Use scanner_family_producer.run_once; no standalone CLI.')


if __name__ == '__main__':
    main()