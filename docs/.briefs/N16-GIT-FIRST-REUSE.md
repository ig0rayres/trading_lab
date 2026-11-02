# N16.0 Git First — reuse inventory (Command Panel + Prodígio path)

> 2026-11-02 · Rock EXECUTE · local vendor present

| Capability | Upstream / local | Decision | Tests |
|------------|------------------|----------|-------|
| Strategy phases | `src/strategy_catalog.py` | **Reuse** `list_strategy_states()` for dashboard | `test_strategy_catalog.py` |
| Ledger counts | `ledger_reconcile.ledger_snapshot` | **Reuse** | `test_ledger_reconcile.py` |
| Prodigy rank | `src/prodigy_rank.py` (research-only) | **Reuse** output file `intelligence/prodigy-top10-latest.json` | `test_prodigy_rank.py` |
| Dashboard UI | `v4_web_dashboard.py` | **Adapt** HTML + `/api/status` `command_panel` | `test_v4_web_dashboard.py` |
| Paper path | `signal_paper_runner.py` | **Reuse**; no new submit | `test_signal_paper_runner.py` |
| trader-* | `vendor/day-trader-skill` @ `2301349` | **No rewrite**; N16.2 only if ingest gap documented | parity via existing tests |

GitHub `main` SHA: not re-fetched this run (offline OK per AGENTS.md if noted).

Gap requiring new code: read-only aggregation in `trading_dashboard_data.command_panel` only.
