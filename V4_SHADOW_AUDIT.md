# Trading Lab v4 Shadow audit (2026-10-29)

Added `src/v4_shadow_audit.py` as a deterministic, local, append-only evaluation journal for B3/crypto *hypothetical* outcomes. It consumes valid local paper intents plus caller-provided post-intent bars through the existing `v4_shadow_marks.evaluate_shadow` engine.

- Atomic process lock with `fcntl`; distinct strategy/market/signal identity; duplicate evaluations blocked.
- Hash-chained JSONL records, fsync after append; corruption blocks new entries, but the chain **cannot** prevent rewriting/truncating an entire file (requires external anchor and backup).
- Read-only report: separate hypothetical closed P&L in BRL, never actual broker realized P&L.
- `scripts/run.sh v4-shadow-audit --ledger /app/reports/shadow/v4-outcomes.jsonl` prints integrity and counts; no order submission.
- Direct API `append_evaluation(intent, bars, target_brl=..., ledger=...)` is not wired to any live feed or broker. No claim of autonomous evaluation until a verified feed is integrated.
- Risks: supplied bar `verified=True` is self-attested; price provenance is not independently checked. No live trading.

Local test suite: 242 passing (`PYTHONPATH=.:src python -m pytest -q`). This is **not** an operational acceptance or final release.
