# N32.0 Git First — control_flags parity in paper runner (Feature 7)

> Rock PLAN N32 · 2026-11-16 · frente `front/n27-alpaca-loop` · **no vendor bump**

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Local `vendor/day-trader-skill` | **not a git checkout** on this worktree — treat pin above as the only SHA |
| GitHub `Jakeschincariol/day-trader-skill` `main` | **not re-checked** (fail-closed: do not claim current main) |

No vendor upgrade in N32. Do not copy upstream scoring. Do not invent Tá Barato / momentum / Prodígio thresholds.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| Panel âncoras | `src/risk_control_flags.py` `fetch_control_flags`, `brl_from_cents`, `TIGHT_DEFAULTS` | **Reuse / call** | N22 fail-closed defaults (R$ 5.000 / R$ 50 / 3) when DB missing | `tests/test_risk_control_flags.py` |
| Gate B FX split | `src/gate_b_risk.py` `config_for_fx` / `evaluate_signed_signal` | **Call / mirror** | Already converts cents→BRL→USD via existing `fx`; N32 does not invent an FX CLI | `tests/test_feature7_anchor_ceilings.py` `test_feature7_anchor_gate_b_tight_capital_config_blocks_large_ticket` |
| Portfolio ceilings | `src/portfolio_risk_v4.py` `resolve_limits` / `evaluate` | **Call only** | Already reads `control_flags` (N22); keep snapshot path; do not duplicate evaluator | `tests/test_feature7_anchor_ceilings.py` Feature7PortfolioAnchorTests |
| Paper one-shot | `src/signal_paper_runner.py` `risk_check` | **Extend** | Replace `Decimal('10000')` / `50`/`20` USD and hardcoded `>=3` with flags+fx; keep reasons | `tests/test_signal_paper_runner.py` |
| Fila pós–Gate B | `src/paper_gateway_queue.py` | **Do not touch** unless a single import needs `conn_factory` passthrough — default: **leave** | N30 already submits US+CRYPTO | `tests/test_paper_gateway_queue.py` |
| trader-entry/exit/budget/risk/scanner | `src/original.py` | **Reuse / no rewrite** | MIT loader; no scoring copy | `tests/test_vendor_verify.py` |
| Clear / OANDA | `src/demo_broker_adapters.py` | **Do not touch** | ISS-010 / N29.5 | existing gate tests |
| Tá Barato | vendor + sprint **N17** | **Defer** | G-FORM | — |

## Gap (this sprint only)

| Gap | New code? | Notes |
|-----|-----------|-------|
| `risk_check` capital/per-trade USD hardcaps | **Extend** `signal_paper_runner.risk_check` | Parallel to `control_flags`; Feature 7 criterion still `[ ]` |
| `len(positions)>=3` | **Extend** same function | Use `max_open_positions` from flags |
| Prodigy R$ 20 vs R$ 50 | **Reuse** `prodigy_risk_cents` / `max_risk_per_trade_cents` | Same keys as `portfolio_risk_v4._limits_from_flags` |
| New scoring / FX CLI / Clear / OANDA | **No** | Forbidden |

## Security / invariants

- `LIVE_TRADING_ENABLED=false`.
- B3_EQUITY / FOREX stay `NO_DEMO_ACCOUNT_PATH` (zero Alpaca POST).
- Fail-closed: missing DB → `TIGHT_DEFAULTS` (already the project pattern). Do not fall back to 10k USD.

## Deferred (out of N32)

- **N17** — Tá Barato / G-FORM.
- **N29.5 / ISS-010** — Clear B3 + OANDA Practice.
- **N28 / N31** ROADMAP blocks — do not rewrite; do not mark concluída here.
- Vendor pin bump.
