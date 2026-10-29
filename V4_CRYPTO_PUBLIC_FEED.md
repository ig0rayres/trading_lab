# v4 crypto public feed — research only

Introduced `src/v4_crypto_feed.py` and `scripts/run.sh v4-crypto-feed` for read-only Binance public `BTCBRL`, `ETHBRL`, `SOLBRL` OHLC collection.

- Supports 1h, 4h, 1d intervals and bounded history (2–500 requests).
- Strictly validates price data, timestamp ordering and bar interval; excludes incomplete bars based on the caller clock.
- Keeps source URL, raw-response SHA-256, and explicit `SINGLE_PUBLIC_EXCHANGE_RESPONSE` provenance metadata.
- Does NOT mark vendor candles as independently verified; no live trading or Paper authorization is granted.
- Does NOT validate actual public API availability here; tests mock response payloads.
- B3 and US reliable live data connectors, persistence/retry scheduling, reconciliation, FX and broker execution remain pending.

Local tests: `PYTHONPATH=.:src pytest -q` -> 262 passed. No deployment or live orders.
