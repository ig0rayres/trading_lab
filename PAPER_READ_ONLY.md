# Alpaca Paper integration: read-only v1.4

This release adds `paper-audit`, a strictly read-only diagnostic for an Alpaca paper account. It makes three GET requests: `/v2/account`, `/v2/positions`, `/v2/orders?status=open&limit=500`. It contains no order placement, cancellation, replacement, or closing functions.

## Required environment (configure in EasyPanel secrets; never in the repository)

- `ALPACA_API_KEY` and `ALPACA_SECRET_KEY`: credentials for the PAPER account only.
- `ALPACA_BASE_URL=https://paper-api.alpaca.markets`
- `ALPACA_PAPER_TRADE=true`
- `LIVE_TRADING_ENABLED=false`
- `USD_BRL_REFERENCE`: explicit BRL per one USD reference, e.g. provide the rate you chose (not an automatic live lookup).

A paper account's `$5000` balance does NOT mean a BRL 5000 strategy budget. The audit computes capital ceiling `5000 / USD_BRL_REFERENCE` USD, and planned risk `50 / USD_BRL_REFERENCE` USD. It does not alter the broker's balance or buying power. The account is denominated in USD.

## Commands

`/app/scripts/run.sh test-local`

`/app/scripts/run.sh paper-audit --output /app/reports/paper/paper-audit.json`

The audit reports account status, balance, positions, market exposure and open orders; it does not print credentials or API responses wholesale. The output is still account-related and should be treated as private. If the FX rate is missing or any safety variable mismatches, it fails closed *before* network access.

## Safety boundary

`paper_execution_authorized: false` and `live_execution_authorized: false` are ALWAYS returned. A GET-only diagnostic cannot prove that risk per trade was correctly computed or enforce future trading limits. Risk and position caps are intended goals for a later separately tested execution gate, not claims that the broker enforces them. Swing positions may gap through stops. No automatic orders are included in this package.
