# v2.8 Alpaca Paper gateway — controlled beta

Git First: reviewed `trader-broker/SKILL.md` and `trader-risk/SKILL.md` in `Jakeschincariol/day-trader-skill` main. Their per-order approval and risk gate principle is preserved. Upstream order tools depend on Claude approval cards and were not reused as a headless order executor.

## What is shipped

`/app/scripts/run.sh paper-gateway --ticket /app/reports/paper/ticket.json` evaluates **one manually curated** News First ticket. By default, it returns PREVIEW_ONLY with zero orders. The ticket must come from an independently verified event and a fresh market observation; the current `news-cycle` signals do not satisfy this. Ticket schema: symbol, side=buy, asset_class=us_equity, event_id, primary_source_url, event_verified_at_utc, price_observed_at_utc, entry, stop, target, quantity (integer), event_verified=true, reaction_confirmed=true, news_first=true. This is a format, not a recommendation to fabricate confirmations.

Two opt-in gates are required before any Paper submission: `PAPER_EXECUTION_ENABLED=true` *in the EasyPanel environment* and a one-order `--confirm-fingerprint` matching the preflight preview, in addition to existing ALPACA_PAPER_TRADE=true, LIVE_TRADING_ENABLED=false, paper-only URL, valid credentials and FX. No submission from install, startup, tests, news-cycle or daemon. Only LONG US equities supported, bracket limit buy plus stop/take profit. Hard exposure reference BRL 5000 (based on manual USD_BRL_REFERENCE), max 3 positions, no existing open orders, cash-funded only, max planned BRL 50 stop risk and >=2:1 target-to-stop. Actual losses can exceed stop risk due to gaps and fills.

## Limitations — do not enable live trading

This is **NOT a fully autonomous operational robot**. No primary-source event verification, contemporaneous analyst consensus, live price verification from an independent feed, event-to-order bridge, order monitoring, end-of-day flattening, reconciliation of timeout outcomes or daily realized-loss gate is implemented here. The ticket's evidence/price assertions are currently provided by its creator. No Crypto/SHORT executor. Do not enable PAPER_EXECUTION_ENABLED until remaining validations are completed. Paper orders, if explicitly enabled and submitted, can be filled by Alpaca. Unknown submission outcome must be checked through Alpaca order history by client order ID before any retry. Never use real capital with this build.
