# Trading Lab v4 — integration build (NOT homologated for autonomous trading)

Validated on 2026-10-29: 391 pytest tests plus 11 subtests, offline. Research report publisher now writes component files first and a SHA-256-bound manifest last. Dashboard rejects mixed-cycle snapshots.

Important: this is NOT a final autonomous system. Real network/live-source and Alpaca end-to-end acceptance were not possible without credentials and the deployed environment. B3 and crypto broker Paper execution, consolidated brokerage reconciliation, verified financial P&L, News First automated execution and production deployment acceptance remain outstanding. Trading real intentionally disabled. Preserve existing EasyPanel services until a staged, supervised acceptance test is completed.

This release is a reproducible local research/observability build, not a guarantee of strategy profits or broker execution safety.

Additional local hardening: scheduler invalidates stale published manifest after a failed/blocked/timed-out cycle; maintains status in v4_scheduler.json. Tested for success, failure, and unsafe symlinks. 394 tests and 11 subtests passed locally. No broker or live API execution was performed.

Next integration hardening (2026-10-29): read-only dashboard's displayed research_cycle status is now derived from verified research_overview, not an unchecked raw manifest. Tampered component files cannot retain a visible trusted success status. Regression test added. 395 pytest tests and 11 subtests passed locally. This does not close broker/network/execution acceptance gaps.
