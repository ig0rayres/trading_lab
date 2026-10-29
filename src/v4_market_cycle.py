"""Read-only multi-market candle cycle. Fail-closed, never submits trades."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from .v4_crypto_feed import fetch_public_candles as fetch_crypto
    from .v4_equity_feed import fetch_public_candles as fetch_equity
except ImportError:
    from v4_crypto_feed import fetch_public_candles as fetch_crypto
    from v4_equity_feed import fetch_public_candles as fetch_equity

DEFAULT_UNIVERSE = [('US_EQUITY', 'AAPL'), ('B3_EQUITY', 'ITUB4'), ('CRYPTO', 'BTCBRL')]


def collect(universe=None, *, equity_fetch=None, crypto_fetch=None):
    equity_fetch = equity_fetch or fetch_equity
    crypto_fetch = crypto_fetch or fetch_crypto
    results, errors = {}, {}
    seen = set()
    for market, symbol in (DEFAULT_UNIVERSE if universe is None else universe):
        key = f'{market}:{symbol}'
        if key in seen:
            errors[key] = 'DUPLICATE_UNIVERSE_ENTRY'
            continue
        seen.add(key)
        try:
            if market == 'CRYPTO':
                row = crypto_fetch(symbol=symbol, interval='1h')
            elif market in ('US_EQUITY', 'B3_EQUITY'):
                row = equity_fetch(market=market, symbol=symbol, interval='1d')
            else:
                raise ValueError('UNSUPPORTED_MARKET')
            if row.get('market') != market or row.get('symbol') != symbol or row.get('usable_for_live_trading') is not False:
                raise ValueError('UNSAFE_OR_WRONG_FEED')
            results[key] = row
        except Exception as exc:
            errors[key] = f'{type(exc).__name__}: {exc}'
    return {'status': 'RESEARCH_ONLY' if not errors else 'PARTIAL_OR_BLOCKED',
            'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'results': results, 'errors': errors,
            'usable_for_live_trading': False, 'automatic_order_submission': False}


def main():
    parser = argparse.ArgumentParser(description='Read-only multi-market candle collector')
    parser.add_argument('--output', default='/app/reports/v4_market_cycle.json')
    args = parser.parse_args()
    result = collect()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'markets_collected': len(result['results']),
                      'errors': result['errors'], 'output': str(output)}, indent=2))
    return 0 if not result['errors'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
