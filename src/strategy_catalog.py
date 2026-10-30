"""Strategy family phases (Feature 4). Read-only promotion; insert-if-missing seed only."""
from __future__ import annotations

import os
import re
from typing import Callable

KNOWN_STRATEGY_KEYS = frozenset(
    {
        'news_first',
        'momentum',
        'ta_barato',
        'signal_copy',
        'prodigy_15d',
        'orb',
        'mean_reversion',
    }
)

DEFAULT_PHASE_BY_KEY = {
    'news_first': 'research',
    'momentum': 'research',
    'ta_barato': 'research',
    'prodigy_15d': 'research',
    'signal_copy': 'paper_limited',
    'orb': 'shadow',
    'mean_reversion': 'shadow',
}

NEVER_PAPER_KEYS = frozenset({'orb', 'mean_reversion'})
NON_PAPER_PHASES = frozenset({'research', 'shadow'})
PAPER_PHASES = frozenset({'paper_limited', 'paper_validated'})

_KEY_RE = re.compile(r'^[a-z][a-z0-9_]{1,62}$')


def normalize_strategy_key(raw) -> str | None:
    if raw is None:
        return None
    key = str(raw).strip().lower()
    if not _KEY_RE.fullmatch(key):
        return None
    return key


def ensure_strategy_defaults(conn_factory: Callable | None = None, *, strict: bool = False) -> None:
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        if strict:
            raise RuntimeError('LEDGER_DATABASE_URL is not set')
        return
    try:
        with conn_factory() as conn:
            for strategy_key, phase in DEFAULT_PHASE_BY_KEY.items():
                with conn.cursor() as cur:
                    cur.execute(
                        'INSERT INTO strategy_states (strategy_key, phase) VALUES (%s, %s) '
                        'ON CONFLICT (strategy_key) DO NOTHING',
                        (strategy_key, phase),
                    )
            conn.commit()
    except Exception:
        if strict:
            raise
        return


def fetch_strategy_phase(strategy_key: str, conn_factory: Callable | None = None) -> str | None:
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    ensure_strategy_defaults(conn_factory)
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT phase FROM strategy_states WHERE strategy_key = %s AND deleted_at IS NULL',
                    (strategy_key,),
                )
                row = cur.fetchone()
        return str(row[0]) if row else None
    except Exception:
        return None


def resolve_strategy_phase(
    strategy_key: str,
    *,
    strategy_phase: str | None = None,
    conn_factory: Callable | None = None,
) -> str | None:
    if strategy_phase is not None:
        return strategy_phase
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return None
    return fetch_strategy_phase(strategy_key, conn_factory)


def gate_b_strategy_reject(
    signal: dict,
    *,
    strategy_phase: str | None = None,
    conn_factory: Callable | None = None,
) -> str | None:
    """Return reject_code or None if strategy catalog allows proceeding to trader-risk."""
    raw_key = signal.get('strategy_key')
    if raw_key is None or raw_key == '':
        return 'STRATEGY_KEY_REQUIRED'
    key = normalize_strategy_key(raw_key)
    if key is None or key not in KNOWN_STRATEGY_KEYS:
        return 'STRATEGY_UNKNOWN'
    if key in NEVER_PAPER_KEYS:
        return 'STRATEGY_NOT_PAPER'
    phase = resolve_strategy_phase(key, strategy_phase=strategy_phase, conn_factory=conn_factory)
    if phase is None:
        return 'STRATEGY_PHASE_UNKNOWN'
    if phase in NON_PAPER_PHASES:
        return 'STRATEGY_PHASE_BLOCKED'
    if phase not in PAPER_PHASES:
        return 'STRATEGY_PHASE_UNKNOWN'
    return None
