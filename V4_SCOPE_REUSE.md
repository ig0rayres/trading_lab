# Full-scope reuse inventory and honest readiness (29 Oct 2026)

The branch/user base includes the original 11-skill day-trader research tools and iterative Trading Lab implementations. Prefer reuse instead of another scanner rewrite. Modules already bundled:

- Scanner/market opportunities: `market_opportunities.py`, `swing_radar.py`, `day_radar.py`, `strategy_intelligence.py`, original research scanners.
- News and event checks: `news_catalog.py`, `news_cycle.py`, `event_verifier.py`, `news_first_sim.py`, `news_audit.py`.
- External signal research: `c2_signal_feed.py`, `signal_copy.py`, `tradingview_webhook.py`, `tradingview_worker.py`, `provider_rank.py`, `prodigy_rank.py`.
- Simulation and replay: `shadow_journal.py`, `v4_shadow_broker.py`, `v4_shadow_marks.py`, `time_machine_audit.py`, `ten_day_replay.py`, `evolution_engine.py`.
- Existing Alpaca Paper flow: `paper_gateway.py`, `paper_audit.py`, `paper_reconcile.py`, `paper_monitor.py`, `signal_paper_runner.py`.
- Market research: `v4_market_cycle.py` using `v4_equity_feed.py` and `v4_crypto_feed.py`.
- NEW: `v4_strategy_pipeline.py` transforms a saved unified market-cycle output into `market_opportunities` Shadow-only observations, explicitly preserving missing quality, catalyst, volume and independent provenance checks.

Offline usage: first run `v4-market-cycle --output /app/reports/v4_market_cycle.json`, then `v4-strategy-pipeline --input /app/reports/v4_market_cycle.json --output /app/reports/v4_strategy_observations.json`.

Not production-homologated: live market feed verification, professional-quality market data/corporate action handling, real news provider availability, independently authenticated external signals, C2 API, central risk enforcement across *all* executors and services, atomic portfolio state, durable order workflow, broker order fill/exit reconciliation, B3/crypto simulated execution latency, dashboard web UX and end-to-end deployment validation. Local tests do not prove any of these. No unattended auto-trading release is authorized, and no live-trading functionality is enabled. Alpaca test order was manual and is not a News First proof.

The initial GitHub repo `Jakeschincariol/day-trader-skill` is a research toolkit and expressly does not autonomously place orders; retain its research-first safety model. Avoid copying the repo into this tree without license/source and conflict review.
