# Trading Lab v4 - engineering handoff (not production acceptance)

Validated offline: 358 passed, 11 subtests passed (PYTHONPATH=src:. pytest -q), 2026-10-29. Sources compile. No orders sent.

What works locally: research feeds and strategy pipeline (fixtures), risk preview and conservative blocking, shadow audit, Alpaca observations and activity parsing, FIFO ledger based on supplied records, read-only local dashboard.

Blocking conditions for declaring a FINAL autonomous product:
1. Verify all external feeds and operational news/provider signal ingestion in the actual deployment and handle outages.
2. End-to-end authenticated signal -> decision -> globally reconciled risk -> actual Paper broker order -> fill -> exits with broker confirmations.
3. B3 and crypto Paper execution and positions / orders / cash reconciliation, with closed-loop tests.
4. Authenticate dashboard publicly; integrate actual P&L verified with broker activities and fees.
5. Homologate both EasyPanel services including their storage volumes, entrypoints, and key management.

Do not upgrade the current EasyPanel services from this package or enable live trading. No credentials are included.
