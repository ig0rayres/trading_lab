"""Apply or rollback SQL migrations for the paper ledger. No credentials in repo."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / 'migrations'
VERSION = '001_ledger'
VERSION_TRIGGERS = '002_triggers'
VERSION_PROVIDER_APPROVALS = '003_signal_provider_approvals'


def dsn():
    url = os.environ.get('LEDGER_DATABASE_URL', '').strip()
    if not url:
        raise RuntimeError('LEDGER_DATABASE_URL is not set')
    return url


def _connect():
    import psycopg

    return psycopg.connect(dsn(), autocommit=False)


def _execute_migration(filename: str) -> None:
    sql = (MIGRATIONS_DIR / filename).read_text(encoding='utf-8')
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def _seed_operational_defaults() -> None:
    try:
        from operational_defaults import ensure_operational_defaults

        with _connect() as conn:
            ensure_operational_defaults(conn)
            conn.commit()
    except Exception as exc:
        err = str(exc).lower()
        if 'demo_operation_on' in err or 'market_controls' in err or 'undefinedtable' in err:
            return
        if 'not set' in err:
            return
        raise


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
    applied_any = False
    if not st['applied']:
        _execute_migration('001_ledger_up.sql')
        applied_any = True
    if not status()['triggers_applied']:
        _execute_migration('002_triggers_up.sql')
        applied_any = True
    if not status()['provider_approvals_applied']:
        _execute_migration('003_signal_provider_approvals_up.sql')
        applied_any = True
    _seed_strategy_catalog()
    _seed_operational_defaults()
    status_label = 'applied' if applied_any else 'already_applied'
    return {'status': status_label, 'version': VERSION, 'strategy_seed': 'ok'}


def rollback():
    st = status()
    if not st['applied'] and not st['triggers_applied'] and not st['provider_approvals_applied']:
        return {'status': 'not_applied', 'version': VERSION}
    if st['provider_approvals_applied']:
        _execute_migration('003_signal_provider_approvals_down.sql')
    if st['triggers_applied']:
        _execute_migration('002_triggers_down.sql')
    if st['applied']:
        _execute_migration('001_ledger_down.sql')
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
                cur.execute(
                    'SELECT version FROM schema_migrations WHERE version = %s',
                    (VERSION_TRIGGERS,),
                )
                row_triggers = cur.fetchone()
                cur.execute(
                    'SELECT version FROM schema_migrations WHERE version = %s',
                    (VERSION_PROVIDER_APPROVALS,),
                )
                row_approvals = cur.fetchone()
            except psycopg.errors.UndefinedTable:
                row = None
                row_triggers = None
                row_approvals = None
    return {
        'version': VERSION,
        'applied': row is not None,
        'triggers_applied': row_triggers is not None,
        'provider_approvals_applied': row_approvals is not None,
    }


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
