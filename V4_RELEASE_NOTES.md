# Trading Lab v4.0 — release-candidate research foundation (NOT autonomous-ready)

## Delivered and actually tested
- Preserves all modules and gateway of v3.9. No change to paper gateway, order submission code, or live-trading flag.
- Prodígios: trailing 15-day discovery instead of 60-day; >=5 closed trades, >=3 distinct trading days, and conservative shrunk win rate. Historical P/L is NOT verified net P/L and discovery never grants copy approval.
- `opportunity-scan --input <file>`: offline/data-fed cross-market Ta Barato Demais watchlist over 6+ ordered and timestamped price bars, for US equities, B3 equities and crypto. Different drawdown thresholds by market; `SHADOW_ONLY` output, with quality/catalyst/reversal caveats and no paper promotion.
- `dashboard-data --root /app/reports`: read-only JSON metrics derived from journal and broker snapshots, deduplicated by `client_order_id`; missing P&L is `null`, not fabricated.
- `v4-readiness --reports /app/reports`: safety posture and explicit blockers, without printing API secrets.
- Offline tests: `PYTHONPATH=src python3 -m unittest discover -s tests -q`.

## Critical gaps — prohibit autonomous production declaration
- No live market-data and news ingestion/feed verification for all 3 markets. The opportunity screen requires external **completed** bars and independently researched fundamentals/catalyst.
- No B3 broker execution adapter or verified B3 price-provider; B3 remains Shadow.
- Alpaca crypto cannot safely reuse stock bracket orders; lacks dedicated stop/target watcher and failover. Crypto remains Shadow.
- Scanner/news/rank/signal to broker end-to-end automation has not been proven. News First deliberately requires real verified events and price reaction.
- Centralized daily/weekly loss and cross-market exposure limits are not implemented end-to-end and cannot be assumed from standalone risk functions.
- Strategy promotion requires historical out-of-sample results, costs/slippage, and independent observation. No strategy auto-promoted.
- Real Alpaca Paper order from earlier session was manually sent, not tested by this offline release.
- Some vendor code `/app/vendor/day-trader-skill` is mounted on the server but NOT present in this ZIP. GitHub upstream README can be accessed; exact upstream main commit and installed vendor commit not verified. No claim of full vendor parity.

## Test and deployment sequence
1. Back up both EasyPanel services, envs and volumes; keep previous image for rollback.
2. Deploy ZIP in a staging service with `LIVE_TRADING_ENABLED=false`, `PAPER_SIGNAL_AUTO_ENABLED=false`; do not switch main or webhook simultaneously.
3. Run `test-local` and `v4-readiness`. `dashboard-data` is strictly read only; expected `null` P&L until closed snapshots exist.
4. Run `opportunity-scan` with independently verified, time-zoned OHLCV fixtures. Shadow only.
5. Verify persistent mounts and Paper monitor separately before promoting this build. Never claim first deployment until actual environment checks pass.
