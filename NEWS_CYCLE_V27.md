# News First dual-market cycle (research only)

Git First: reused Alpaca GET news audit, catalog, evidence triage and internal journal. GitHub main checked: trader-news/news.py, trader-entry/entry.py (LONG-only), trader-analyst/facts.py.

Run in EasyPanel after deploy:

    /app/scripts/run.sh news-cycle --days 3 --pages 20

This runs independent pipelines for stocks (AAPL, MSFT, NVDA, AMD, TSLA, PLTR) and crypto (BTCUSD, ETHUSD), preserving each cohort's reports in /app/reports/news/cycle/<market>/ and a common summary in /app/reports/news/cycle/latest.json. Any incomplete pagination causes downstream catalog generation to fail closed. This may require shorter --days to fit 20 pages. The script uses existing Alpaca historical news GET only, not trading API endpoints.

This command makes NO TRADES, not even internally. A review journal records NO_TRADE decisions for unverified events. It does not compute fills, risk, P&L, or verified primary-source news. It is a live/recent market-data pipeline, not a profitable strategy or verified trade simulator. News availability and BTC/ETH coverage depend on the Alpaca account and provider.

Risk: zero order calls, no live execution authorization. Do not add execution permissions before source verification, timely price data, realistic portfolio simulation, and explicit authorization.
