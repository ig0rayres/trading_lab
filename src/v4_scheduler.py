"""Fail-closed scheduling for the v4 *research only* pipeline.

Never imports broker code. Non-overlapping runs and explicit status reports make
unattended research observable without silently enabling trade submissions.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def lock_once(path):
    """Acquire exclusive persistent lock; release by closing its descriptor."""
    import fcntl
    lock = Path(path)
    if lock.is_symlink():
        raise ValueError('UNSAFE_LOCK_PATH')
    lock.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock), os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException:
        os.close(fd)
        raise
    return fd


def run_cycle(universe, output_dir, *, timeout=180, runner=None):
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        return {'status': 'BLOCKED_LIVE_FLAG', 'orders_sent': 0, 'exit_code': 2}
    command = [sys.executable, str(Path(__file__).with_name('v4_run_once.py')),
               '--universe', str(universe), '--output-dir', str(output_dir)]
    if runner is None:
        runner = subprocess.run
    try:
        result = runner(command, capture_output=True, text=True, timeout=timeout, check=False)
        code = result.returncode
        status = 'FINISHED_RESEARCH' if code == 0 else 'FAILED_OR_BLOCKED'
        return {'status': status, 'exit_code': code, 'orders_sent': 0,
                'output_excerpt': (result.stdout or '')[-500:]}
    except subprocess.TimeoutExpired:
        return {'status': 'CYCLE_TIMEOUT', 'exit_code': 124, 'orders_sent': 0}


def invalidate_stale_manifest(folder, status):
    """Prevent a failed research cycle from leaving the previous success visible."""
    if status.get('exit_code') == 0 and status.get('status') == 'FINISHED_RESEARCH':
        return
    manifest = Path(folder) / 'v4_manifest.json'
    if manifest.is_symlink():
        raise ValueError('UNSAFE_MANIFEST_PATH')
    if manifest.exists():
        manifest.unlink()


def record_status(path, status):
    from v4_run_once import atomic_json
    payload = dict(status, timestamp_utc=datetime.now(timezone.utc).isoformat(),
                   scheduler_role='RESEARCH_ONLY', execution_authorized=False)
    atomic_json(Path(path), payload)


def main(argv=None):
    p = argparse.ArgumentParser(description='Run non-overlapping research-only cycles')
    p.add_argument('--universe', required=True)
    p.add_argument('--output-dir', required=True)
    p.add_argument('--interval-seconds', type=int, default=900)
    p.add_argument('--timeout-seconds', type=int, default=180)
    p.add_argument('--once', action='store_true')
    args = p.parse_args(argv)
    if not (30 <= args.interval_seconds <= 86400 and 5 <= args.timeout_seconds < args.interval_seconds):
        p.error('timeout must be between 5 and interval; interval must be >=30')
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        return 2
    folder = Path(args.output_dir)
    if folder.is_symlink():
        return 2
    try:
        lock_fd = lock_once(folder / '.v4-research.lock')
    except (OSError, ValueError):
        return 2
    try:
        while True:
            start = time.monotonic()
            status = run_cycle(args.universe, folder, timeout=args.timeout_seconds)
            invalidate_stale_manifest(folder, status)
            record_status(folder / 'v4_scheduler.json', status)
            print(json.dumps(status), flush=True)
            if args.once:
                return 0 if status['exit_code'] == 0 else 2
            time.sleep(max(0, args.interval_seconds - (time.monotonic() - start)))
    finally:
        os.close(lock_fd)


if __name__ == '__main__':
    raise SystemExit(main())
