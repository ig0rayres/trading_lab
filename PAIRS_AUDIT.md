# Pairs robustness screen — v1.1

Reads v1.0 pair_trades.csv and summary.json **without fetching or trading**. No baseline strategy modifications.

Run in EasyPanel after upgrading the image (preserve /app/reports and /app/vendor):

```sh
/app/scripts/run.sh test-local
/app/scripts/run.sh pair-robustness --report /app/reports/external/v10 --output /app/reports/research/pairs-v11.json
```

`additional_one_way_bps_per_leg`: amounts charged IN ADDITION to v1.0 fee/slippage, on each of the two legs. For example, an extra 5bp per side on each leg subtracts 0.10 percentage points from pair notional return. Values do not model locate availability or true short-borrow rates.

`earlier`/`later` is a descriptive date split, not independent holdout. `leave_one_pair_out` tests concentration but small samples prevent edge claims. Do not promote to live trading. Next prerequisite: multi-year source, cointegration stability tests without look-ahead, actual short availability, full portfolio backtest.
