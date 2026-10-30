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


def apply():
    st = status()
    if st['applied']:
        return {'status': 'already_applied', 'version': VERSION}
    sql = (MIGRATIONS_DIR / '001_ledger_up.sql').read_text(encoding='utf-8')
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    return {'status': 'applied', 'version': VERSION}


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
