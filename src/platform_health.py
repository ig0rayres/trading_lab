"""Automated platform health probes; persisted snapshot (no secrets)."""
from __future__ import annotations

import json
import os
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKER_STAMP_NAME = 'tv-worker-last.json'
HEALTH_SNAPSHOT_NAME = 'platform-health-latest.json'
REL_OPS = Path('ops')
COMPONENT_IDS = ('ledger', 'worker', 'webhook', 'queue', 'dashboard')

STATUS_OK = 'ok'
STATUS_DEGRADED = 'degraded'
STATUS_DOWN = 'down'
STATUS_SKIPPED = 'skipped'


def _ops_dir(root: Path) -> Path:
    return root / REL_OPS


def worker_stamp_path(root: Path) -> Path:
    return _ops_dir(root) / WORKER_STAMP_NAME


def health_snapshot_path(root: Path) -> Path:
    return _ops_dir(root) / HEALTH_SNAPSHOT_NAME


def write_worker_stamp(root: Path, *, processed: int) -> None:
    path = worker_stamp_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'at': datetime.now(timezone.utc).isoformat(),
        'processed': processed,
    }
    _atomic_write(path, payload)


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.health-', suffix='.json')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(data)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _age_seconds(iso_ts: str | None) -> float | None:
    if not iso_ts:
        return None
    try:
        stamp = datetime.fromisoformat(str(iso_ts).replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - stamp).total_seconds()
    except (TypeError, ValueError):
        return None


def probe_ledger(env: dict[str, str] | None = None) -> dict[str, Any]:
    env = env or os.environ
    if not env.get('LEDGER_DATABASE_URL', '').strip():
        return {'id': 'ledger', 'status': STATUS_DEGRADED, 'detail': 'LEDGER_DATABASE_URL unset'}
    try:
        from ledger_store import connect

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1')
                cur.fetchone()
        return {'id': 'ledger', 'status': STATUS_OK, 'detail': 'connected'}
    except Exception as exc:
        return {'id': 'ledger', 'status': STATUS_DOWN, 'detail': type(exc).__name__}


def probe_worker(root: Path, env: dict[str, str] | None = None) -> dict[str, Any]:
    env = env or os.environ
    path = worker_stamp_path(root)
    if not path.is_file():
        return {'id': 'worker', 'status': STATUS_DEGRADED, 'detail': 'no worker stamp yet'}
    try:
        stamp = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return {'id': 'worker', 'status': STATUS_DOWN, 'detail': 'stamp unreadable'}
    age = _age_seconds(stamp.get('at'))
    max_age = float(env.get('PLATFORM_HEALTH_WORKER_MAX_SEC', '120'))
    if age is None:
        return {'id': 'worker', 'status': STATUS_DOWN, 'detail': 'stamp missing time'}
    if age > max_age:
        return {
            'id': 'worker',
            'status': STATUS_DEGRADED,
            'detail': 'last run %.0fs ago' % age,
        }
    return {
        'id': 'worker',
        'status': STATUS_OK,
        'detail': 'processed=%s' % stamp.get('processed', 0),
    }


def probe_webhook(env: dict[str, str] | None = None) -> dict[str, Any]:
    env = env or os.environ
    url = env.get('WEBHOOK_HEALTH_URL', '').strip()
    if not url:
        return {'id': 'webhook', 'status': STATUS_SKIPPED, 'detail': 'WEBHOOK_HEALTH_URL unset'}
    req = urllib.request.Request(url, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            code = getattr(resp, 'status', None) or resp.getcode()
        if 200 <= int(code) < 300:
            return {'id': 'webhook', 'status': STATUS_OK, 'detail': 'http %s' % code}
        return {'id': 'webhook', 'status': STATUS_DEGRADED, 'detail': 'http %s' % code}
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return {'id': 'webhook', 'status': STATUS_OK, 'detail': 'reachable http %s' % exc.code}
        return {'id': 'webhook', 'status': STATUS_DEGRADED, 'detail': 'http %s' % exc.code}
    except Exception as exc:
        return {'id': 'webhook', 'status': STATUS_DOWN, 'detail': type(exc).__name__}


def probe_queue(root: Path, env: dict[str, str] | None = None) -> dict[str, Any]:
    env = env or os.environ
    pending = Path(env.get('TV_QUEUE_DIR', str(root / 'webhooks' / 'pending')))
    if not pending.is_dir():
        return {'id': 'queue', 'status': STATUS_OK, 'detail': 'pending=0'}
    files = list(pending.glob('*.json'))
    stale_sec = float(env.get('PLATFORM_HEALTH_QUEUE_STALE_SEC', '3600'))
    now = datetime.now(timezone.utc)
    stale = 0
    for path in files:
        try:
            age = (now - datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)).total_seconds()
            if age > stale_sec:
                stale += 1
        except OSError:
            stale += 1
    if stale:
        return {
            'id': 'queue',
            'status': STATUS_DEGRADED,
            'detail': 'pending=%s stale=%s' % (len(files), stale),
        }
    return {'id': 'queue', 'status': STATUS_OK, 'detail': 'pending=%s' % len(files)}


def aggregate_overall(components: list[dict[str, Any]]) -> str:
    statuses = {c['status'] for c in components if c['status'] != STATUS_SKIPPED}
    if STATUS_DOWN in statuses:
        return STATUS_DOWN
    if STATUS_DEGRADED in statuses:
        return STATUS_DEGRADED
    if not statuses:
        return STATUS_DEGRADED
    return STATUS_OK


def run_probes(root: Path, env: dict[str, str] | None = None) -> dict[str, Any]:
    env = env or os.environ
    components = [
        probe_ledger(env),
        probe_worker(root, env),
        probe_webhook(env),
        probe_queue(root, env),
        {'id': 'dashboard', 'status': STATUS_OK, 'detail': 'probe_runner_active'},
    ]
    overall = aggregate_overall(components)
    payload = {
        'schema_version': 'platform-health-1',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'overall': overall,
        'components': components,
    }
    _atomic_write(health_snapshot_path(root), payload)
    return payload


def load_health_snapshot(root: Path) -> dict[str, Any] | None:
    path = health_snapshot_path(root)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            return None
        return data
    except (OSError, ValueError, TypeError):
        return None


def main(argv=None):
    import argparse

    ap = argparse.ArgumentParser(description='Trading Lab platform health probe')
    ap.add_argument('--root', default=os.environ.get('DASHBOARD_ROOT', '/app/reports'))
    args = ap.parse_args(argv)
    root = Path(args.root)
    result = run_probes(root)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())