# N16.0 Git First — reuse inventory (Prodígio + Command Panel)

> Rock N16.0 · 2026-11-02 · `main` @ merge #14/#15

## Pin verification

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `main` (2026-11-02) | `3d0f4ef6986f` (matches pin) |
| Host submodule `vendor/day-trader-skill` (if present) | must match pin for parity tests |

No vendor upgrade in N16.0.

## Reuse inventory

| Capability | Path | Decision | Tests |
|------------|------|----------|-------|
| Prodigy rank (research) | `src/prodigy_rank.py` | **Reuse** | `tests/test_prodigy_rank.py` |
| Rank output → panel | `intelligence/prodigy-top10-latest.json` | **Reuse** | `test_v4_web_dashboard.py` |
| Sign / validate signal | `src/signal_copy.py` | **Reuse**; add `strategy_key=prodigy_15d` | `tests/test_signal_copy.py` |
| Paper one-shot | `src/signal_paper_runner.py` | **Reuse**; `PRODIGY_PROVIDERS` for R$20 tier | `tests/test_signal_paper_runner.py` |
| Gate B phase | `src/strategy_catalog.py` + `gate_b_risk.py` | **Reuse**; operator promotes `prodigy_15d` | `tests/test_gate_b_risk.py` |
| Fila worker | `paper_gateway_queue.process_after_gate_b` | **Reuse** optional Caminho B | `tests/test_paper_gateway_queue.py` |
| Command Panel | `v4_web_dashboard` + `trading_dashboard_data` | **Done** PR #14 | `tests/test_v4_web_dashboard.py` |
| trader-entry/exit/risk/scanner | `vendor/…` via `original.py` | **No rewrite** | upstream + parity |

## N16.2 gap analysis

| Gap | New code? | Rationale |
|-----|-----------|-----------|
| Rank → signed JSON | **No** | Operador script + `HOMOLOGATION-PRODIGY.md` |
| `prodigy_15d` paper blocked in research | **No** | Operator SQL phase promotion (documented) |
| `PRODIGY_PROVIDERS` env | **No** | Already in `signal_paper_runner.risk_check` |
| Webhook payload mapping rank→symbol | **Maybe** | Only if Caminho B required and reproducible gap; else defer |

**Conclusion:** N16.1 runbook closes operador path without `src/` diff. N16.2 **blocked** unless operador reports Caminho B failure with logs.

## Security / license

- Upstream MIT-style skill tree; no live keys in repo.
- `LIVE_TRADING_ENABLED=false` invariant.
