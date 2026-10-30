"""Minimal Postgres persistence for paper ledger. Append-only fills and ledger rows."""
from __future__ import annotations

import os
from typing import Any

LEDGER_TABLES = (
    'strategy_states',
    'signal_events',
    'risk_decisions',
    'positions',
    'paper_orders',
    'paper_fills',
    'ledger_entries',
    'control_flags',
)

NO_SOFT_DELETE_TABLES = frozenset({'paper_orders', 'paper_fills', 'ledger_entries'})


def connect():
    url = os.environ.get('LEDGER_DATABASE_URL', '').strip()
    if not url:
        raise RuntimeError('LEDGER_DATABASE_URL is not set')
    import psycopg

    return psycopg.connect(url)


def assert_no_soft_delete(table: str, payload: dict[str, Any]) -> None:
    if table in NO_SOFT_DELETE_TABLES and payload.get('deleted_at') is not None:
        raise ValueError('SOFT_DELETE_FORBIDDEN:%s' % table)


def insert_row(conn, table: str, columns: dict[str, Any]) -> None:
    if table not in LEDGER_TABLES:
        raise ValueError('UNKNOWN_TABLE')
    assert_no_soft_delete(table, columns)
    names = list(columns.keys())
    placeholders = ', '.join('%s' for _ in names)
    cols = ', '.join(names)
    sql = 'INSERT INTO %s (%s) VALUES (%s)' % (table, cols, placeholders)
    with conn.cursor() as cur:
        cur.execute(sql, [columns[n] for n in names])
