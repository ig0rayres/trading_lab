# V4 offline price ingestion — 2026-10-29

Added `src/v4_market_data_import.py` and `scripts/run.sh v4-import-prices`.

- Strict CSV schema: `at_utc,open_brl,high_brl,low_brl,close_brl`, UTC-aware timestamps, ascending bars, finite positive prices and sound OHLC ranges.
- Mandatory SHA-256 pin; fail closed if bytes changed; guard against oversized datasets.
- Input prices must already be expressed in BRL (no implicit FX conversion for US/crypto).
- Outputs are locally integrity-checked only. Source authenticity, corporate actions, market calendars, candlestick finality and independent price verification are **not** guaranteed.
- `verified=True` candle field is for compatibility with the existing offline evaluator and must never be interpreted as attested market data. This import does not enable trading.
- No background feed, API subscription, automated reconciliation or broker integration has been implemented by this module.

Full local suite: 254 passing tests. Trading real and deployment remain untouched.
