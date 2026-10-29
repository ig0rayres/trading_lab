# Trading Lab v3.5 — Signal Paper Pilot

Mode: only Alpaca Paper (`https://paper-api.alpaca.markets`). No live trading.

## New CLI
`/app/scripts/run.sh signal-paper --signal /app/data/received-signal.json`

Requires an HMAC-signed JSON from the existing `signal_copy` schema. This is not a webhook server or a scheduler; the signed signal must be delivered to a file. External signals bypass news strategy gates.

Defaults to preview (no orders). To enable one-shot Paper posting, operator must independently set:
`PAPER_SIGNAL_AUTO_ENABLED=true`, `PAPER_EXECUTION_ENABLED=true`, `PAPER_SIGNAL_ACCOUNT_ACK=I_AUTHORIZE_ALPACA_PAPER_ONLY`, and `PAPER_DAILY_RISK_CONFIRMED=true` **only after** independently validating daily loss governance. The last flag is a manual attestation, not automated daily limit enforcement; do not enable for unattended trading.

Safeguards: API credentials Paper-only, no short, capped 3 positions, no other open orders, cash-only, HMAC/TTL check, locked journal, order intent persisted before submission, deterministic client_order_id, fail-closed on unknown response. Bracket stop does not guarantee realized losses, especially gaps. Other open-position stop risk is not fully verified. Per-signal preflight still caps BRL 5k, as upstream signal_copy does; this pilot does NOT apply the proposed BRL 10k target uniformly. Do not claim otherwise.

**Not yet delivered:** webhook listener, autonomous schedule, consolidated daily P&L and aggregate stop risk, quote freshness/slippage check, cash-flow adjusted provider ranking, trade lifecycle monitor. Because of these gaps, this is a controlled one-shot Paper gateway, NOT a fully autonomous production robot.

Run `test-local` and `paper-audit`; never change LIVE_TRADING_ENABLED=false.
