# v2.4 — Conservative News Catalog

Read-only step after a complete `news-audit` run. No broker orders, no trade signals, no earnings surprises inferred.

1. `/app/scripts/run.sh news-audit --start 2026-09-01 --end 2026-09-08 --symbols AAPL,MSFT,NVDA --pages 20`
2. `/app/scripts/run.sh news-catalog`
3. JSON output: `/app/reports/news/catalog.json`

The catalog filters out unrelated articles, tags headline-based potential event categories, and lists URLs, timestamps and mentioned requested symbols. All event classifications are **UNVERIFIED**. The next milestone requires primary-source filings / issuer releases and contemporaneous analyst consensus; only then can a causal price-response study proceed. Incomplete pagination is rejected. Persist the news reports volume if you want durable outputs.
