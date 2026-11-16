# N17.0 Git First — G-FORM ta_barato / momentum

> Rock N17.0 · 2026-11-16 · frente `front/n27-alpaca-loop` · **no vendor bump**

## Pin verification

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Host checkout `/home/igor/cursor/trading-lab/vendor/day-trader-skill` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` (matches pin) |
| GitHub `Jakeschincariol/day-trader-skill` `main` (read-only) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` (same as pin) |

## G-FORM result

| `strategy_key` | Upstream path / symbol search | Decision |
|----------------|----------------------------------|----------|
| `ta_barato` | `rg -i 'barato|ta_barato|demais'` on vendor tree @ pin → **0 hits** | **BLOCKED** — no module to load via `original.py` |
| `momentum` | `rg -i 'momentum'` on vendor tree @ pin → **0 hits** | **BLOCKED** — no module to load via `original.py` |

**Loader scope today:** `src/original.py` only wires `trader-entry`, `trader-exit`, `trader-risk`, `trader-budget`, `trader-scanner` (ORB). No extension point without upstream delivery.

## Reuse inventory (N17.1+)

| Capability | Path | Decision | Rationale | Tests |
|------------|------|----------|-----------|-------|
| Gate B phase block | `src/strategy_catalog.py` `gate_b_strategy_reject` | **Reuse** | `ta_barato`/`momentum` stay `research` → `STRATEGY_PHASE_BLOCKED` | `tests/test_gate_b_risk.py` |
| G-FORM flag | `src/strategy_catalog.py` `UPSTREAM_FORMULA_BLOCKED_KEYS` | **New constant** | Single source for homolog + panel; not a scoring formula | `tests/test_n17_ta_barato.py`, `tests/test_strategy_homolog_traceability.py` |
| Local shadow screen | `src/market_opportunities.py`, `src/v4_strategy_pipeline.py` | **Reuse read-only** | Drawdown radar for **shadow homolog only**; explicitly **not** upstream formula | `tests/test_v4_capabilities.py` |
| Painel homolog | `src/trading_dashboard_data.py` `ta_barato_shadow` | **Extend** | Read `research/opportunities-latest.json`; disclaim G-FORM | `tests/test_n17_ta_barato.py` |
| Paper promotion | — | **Do not** | G-FORM blocked; operator homolog N17.2 deferred | — |

## N17.1 blocked gap (honest)

- **No** integration of vendor scoring — path does not exist at pin.
- **No** new RSI/percentile/drawdown thresholds beyond existing local shadow module (pre-N17 lab code).
- MVP-OP-1.1 release train: **blocked on upstream** for paper; shadow/read-only homolog delivered in N17.5 + pytest.

## Deferred

- **N17.2** operator shadow→paper limitado (requires human + upstream or explicit operator acceptance of local shadow only).
- **N17.4** F-003 orb-parity — skipped per sprint table.
- **N28** — still blocked G-AJUSTE.