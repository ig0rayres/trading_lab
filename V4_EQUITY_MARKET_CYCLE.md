# V4 equity feeds and unified research collection

Implemented read-only Yahoo public chart feed for US and B3 equities, plus a
single cycle invoking the existing Binance BRL crypto feed. This is research
infrastructure, **not verified exchange-grade market data** or authorization to
place trades. No credentials are used. The provider may rate-limit, block,
return delayed prices, or change its schema without notice.

Commands in container:
- `scripts/run.sh v4-equity-feed --market B3_EQUITY --symbol ITUB4`
- `scripts/run.sh v4-equity-feed --market US_EQUITY --symbol AAPL`
- `scripts/run.sh v4-market-cycle --output /app/reports/v4_market_cycle.json`

The cycle's default examples are AAPL / ITUB4 / BTCBRL. It is a one-shot
research command, not a daemon or automatically scheduled process. Errors
cause nonzero exit status, with individual feed failures recorded. Output
includes raw, unverified bars and `usable_for_live_trading=false`.

Rules: validate symbol and response currency; reject ill-formed OHLC, empty
and non-monotonic timestamps; skip missing price bars and unfinished bars;
preserve USD for US equities and BRL for B3 and crypto. No presumed FX.

Validation: 276 automated pytest cases (when last run here) including mocked
transport and failure paths. No live endpoint availability, provider accuracy,
market-hour alignment, stock splits/corporate actions, independent price
validation, rate limiting, persistence security or order execution have been
verified in this work. Do not deploy to trading services yet.
