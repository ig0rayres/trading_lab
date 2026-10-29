# V4 decision-cycle integration (research-only)

This release adds `v4-decision-cycle` to the existing runner. It accepts market-cycle
JSON, optional News First internal simulation JSON, and optional TradingView signed
signals JSON. It calls the existing shadow strategy pipeline and signal intelligence
module and produces one JSON decision report. Source errors propagate to an explicit
partial/blocked status. No broker or order code is imported by this module.

Example from an app container (inputs must already exist):

    /app/scripts/run.sh v4-decision-cycle --market-cycle /app/reports/v4_market_cycle.json --news /app/reports/news_first_signals.json --output /app/reports/v4_decisions.json

`--signed-signals` optionally reads a JSON array of incoming signatures. Validation
requires `SIGNAL_COPY_SECRET` and, when needed, `USD_BRL_REFERENCE`; these are not
embedded into reports. Input JSON is considered untrusted.

This only joins research artifacts. It does **not** launch the news collector, run
continuous polling, prove provider data authenticity, obtain independently validated
market prices, query an Alpaca account, authorize paper execution, or reconcile fills.
Do not deploy as a replacement for the current live services. Keep actual trading
flags disabled and validate all integration steps separately before promotion.

Validation in current workspace: `PYTHONPATH=. pytest -q`: 297 passed.
