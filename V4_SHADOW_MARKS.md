# v4 Shadow OHLC outcome evaluation (2026-10-29)

- `src/v4_shadow_marks.py`: deterministic, offline, **hypothetical** outcome engine for B3/crypto local paper intents.
- Requires a pending local intent and complete, explicitly verified, strictly time-ordered post-intent OHLC bars.
- Stop is conservatively evaluated before target if both touch within a single OHLC bar. Adverse gap through stop is recorded at open, and modeled slippage/fees subtract from return.
- Does **not** fetch or independently attest market data, create broker orders, create actual fills, certify realized P&L, or make entry decisions.
- The engine must not be used to label an unfilled local intent as an actual executed trade. Result prefixes `HYPOTHETICAL_*` and `broker_filled=false` enforce this distinction.
- Local pytest status: 236 passed (`PYTHONPATH=.:src python -m pytest -q`).
- Still required for deploy acceptance: audited live data feeds; reconciled cross-market portfolio snapshots; order routing, fills and exit reconciliation; dashboard; operational validation on both EasyPanel services. Keep live trading off.
