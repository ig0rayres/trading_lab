"""Apply or rollback SQL migrations for the paper ledger. No credentials in repo."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / 'migrations'
VERSION = '001_ledger'


def dsn():
    url = os.environ.get('LEDGER_DATABASE_URL', '').strip()
    if not url:
        raise RuntimeError('LEDGER_DATABASE_URL is not set')
    return url


def _connect():
    import psycopg

    return psycopg.connect(dsn(), autocommit=False)


def _seed_strategy_catalog() -> None:
    from strategy_catalog import DEFAULT_PHASE_BY_KEY, ensure_strategy_defaults

    ensure_strategy_defaults(_connect, strict=True)
    expected = set(DEFAULT_PHASE_BY_KEY.keys())
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT strategy_key FROM strategy_states '
                'WHERE deleted_at IS NULL AND strategy_key = ANY(%s)',
                (list(expected),),
            )
            found = {row[0] for row in cur.fetchall()}
    missing = expected - found
    if missing:
        raise RuntimeError(
            'STRATEGY_SEED_INCOMPLETE: missing %s' % ','.join(sorted(missing))
        )


def apply():
    st = status()
    first_apply = not st['applied']
    if first_apply:
        sql = (MIGRATIONS_DIR / '001_ledger_up.sql').read_text(encoding='utf-8')
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
    _seed_strategy_catalog()
    status_label = 'applied' if first_apply else 'already_applied'
    return {'status': status_label, 'version': VERSION, 'strategy_seed': 'ok'}


def rollback():
    if not status()['applied']:
        return {'status': 'not_applied', 'version': VERSION}
    sql = (MIGRATIONS_DIR / '001_ledger_down.sql').read_text(encoding='utf-8')
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    return {'status': 'rolled_back', 'version': VERSION}


def status():
    import psycopg

    with _connect() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    'SELECT version FROM schema_migrations WHERE version = %s',
                    (VERSION,),
                )
                row = cur.fetchone()
            except psycopg.errors.UndefinedTable:
                row = None
    return {'version': VERSION, 'applied': row is not None}


def main(argv=None):
    ap = argparse.ArgumentParser(description='Paper ledger SQL migrations')
    ap.add_argument('command', choices=('apply', 'rollback', 'status'))
    args = ap.parse_args(argv)
    if args.command == 'apply':
        result = apply()
    elif args.command == 'rollback':
        result = rollback()
    else:
        result = status()
    print(result)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
