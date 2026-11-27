# N30.0 Git First — reuse inventory (Alpaca loop + Prodígio ingest)

> Rock N30.0 · 2026-11-16 · frente `front/n27-alpaca-loop` · **no vendor bump**

## Pin verification

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Host checkout `/home/igor/cursor/trading-lab/vendor/day-trader-skill` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` (matches pin) |

No vendor upgrade in N30. Do not copy upstream scoring into `prodigy_rank.py`.

## Reuse inventory

| Capability | Path | Decision | Rationale | Tests |
|------------|------|----------|-----------|-------|
| Prodigy rank (research) | `src/prodigy_rank.py` | **Reuse** | Collective2 closed-trades window; not execution auth; **no formula copied from vendor** | `tests/test_prodigy_rank.py` |
| Sign / validate signal | `src/signal_copy.py` | **Reuse / call** | HMAC + `ALLOWED_STRATEGIES`; N30.2 maps rank→signed payload | `tests/test_signal_copy.py` |
| Paper one-shot | `src/signal_paper_runner.py` | **Extend** | N30.1: US_EQUITY + CRYPTO submit, restart idempotency, live-looking key → paper host | `tests/test_signal_paper_runner.py` |
| Fila pós–Gate B | `src/paper_gateway_queue.py` | **Reuse / extend** | `process_after_gate_b` delegates to runner when auto allowed | `tests/test_paper_gateway_queue.py` |
| Fase / NEVER_PAPER | `src/strategy_catalog.py` | **Call only** | `gate_b_strategy_reject`; no seed overwrite; `prodigy_15d` stays research until operator promotes | `tests/test_strategy_catalog.py`, `tests/test_gate_b_risk.py` |
| trader-entry/exit/budget/risk/scanner | `vendor/…` via `src/original.py` | **Reuse / no rewrite** | MIT loader; parity via `vendor_verify` | `tests/test_vendor_verify.py`, upstream parity |
| Tá Barato (`ta_barato`) | vendor + sprint **N17** | **Defer** | N30 does not implement momentum/ta scoring path | — |
| Clear / OANDA adapters | `demo_broker_adapters.py` | **Do not touch** | ISS-011 Alpaca-only campaign | existing gate tests |

## N30.1 / N30.2 gap analysis (pre-code)

| Gap | New code? | Notes |
|-----|-----------|-------|
| CRYPTO candidate in auto loop | **Extend** `signal_paper_runner` | Reuse Gate B market routing; no second gateway |
| Restart without duplicate submit | **Extend** runner / queue idempotency | Align with existing ledger + journal stems |
| Rank row → `sign` + ingest | **Wire** (N30.2) | Call `signal_copy` + existing ingest; **no** auto `strategy_states` promotion |
| Copy Prodígio scoring from vendor | **No** | Forbidden; rank stays local research module |
| Bump `day-trader-skill` | **No** | Pin frozen for N30 |

## Security / license

- Upstream skill tree MIT-style; load via `UPSTREAM_DIR` only.
- `LIVE_TRADING_ENABLED=false` invariant; paper host forced when key looks live (N27 tests).
- No Collective2 copy approval path in N30; rank remains `research_only_not_order_auth`.

## Deferred (out of N30 scope)

- **N17** — Tá Barato / upstream scoring recovery.
- **N28** — supervised adjustment (G-AJUSTE).
- **news_first** / **orb** / **mean_reversion** — no phase promotion; NEVER_PAPER unchanged.