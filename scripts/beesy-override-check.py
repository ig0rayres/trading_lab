#!/usr/bin/env python3
"""Project-local entry for Beesy signed overrides (F208/F199).

Delegates to the operator install at ~/.cursor/scripts/beesy-override-check.py
(same contract as beesy-cursor-setup install.sh).
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_TARGET = Path.home() / ".cursor" / "scripts" / "beesy-override-check.py"
if not _TARGET.is_file():
    print(
        f"[beesy-override-check] missing {_TARGET} — run beesy install.sh for this machine.",
        file=sys.stderr,
    )
    raise SystemExit(1)

runpy.run_path(str(_TARGET.resolve()), run_name="__main__")
