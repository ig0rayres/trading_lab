"""Load the original MIT-licensed upstream modules from the existing vendor mount.

Reuses the original functions instead of reproducing their rules. Research-only.
"""
from dataclasses import dataclass
import importlib.util
import os
from pathlib import Path
import subprocess

DEFAULT_REPO = '/app/vendor/day-trader-skill'
SCRIPTS = {
    'entry': ('trader-entry/entry.py', ('evaluate', 'get_chart', 'parse_chart', 'session')),
    'exit': ('trader-exit/exit.py', ('compute', 'parse_stop', 'parse_target')),
    'risk': ('trader-risk/check.py', ('check',)),
    'budget': ('trader-budget/size.py', ('size_trade', 'bracket_order')),
    'scanner': ('trader-scanner/scan.py', ('orb_hit',)),
}

@dataclass
class OriginalModules:
    entry: object
    exit: object
    risk: object
    budget: object
    scanner: object
    commit: str
    path: str


def load_original(repo=None):
    if os.environ.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        raise RuntimeError('LAB_LOCK: LIVE_TRADING_ENABLED must be false; no live trading supported')
    root = Path(repo or os.environ.get('UPSTREAM_DIR') or DEFAULT_REPO).resolve()
    if not root.is_dir():
        raise RuntimeError('Missing original repository at %s. Preserve the /app/vendor volume and run upstream-tests once.' % root)
    loaded = {}
    for name, (relative, required) in SCRIPTS.items():
        f = root / relative
        if not f.is_file():
            raise RuntimeError('Original module missing: %s' % f)
        spec = importlib.util.spec_from_file_location('_trading_lab_original_' + name, str(f))
        if spec is None or spec.loader is None:
            raise RuntimeError('Cannot import %s' % f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        absent = [attr for attr in required if not callable(getattr(mod, attr, None))]
        if absent:
            raise RuntimeError('Original API changed in %s: missing %s' % (f, ', '.join(absent)))
        loaded[name] = mod
    proc = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
    sha = proc.stdout.strip() if proc.returncode == 0 else 'UNVERSIONED_UPSTREAM'
    expected = os.environ.get('UPSTREAM_COMMIT', '').strip()
    if expected and expected != sha:
        raise RuntimeError('Upstream commit differs from pinned UPSTREAM_COMMIT: %s != %s' % (sha, expected))
    return OriginalModules(commit=sha, path=str(root), **loaded)
