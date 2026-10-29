"""Read-only Binance public BRL candle collector for Shadow research.

Public endpoint availability and accuracy are NOT asserted by unit tests.
The newest unfinished bar is never included. No trading or credential use.
"""
import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

ENDPOINT = 'https://api.binance.com/api/v3/klines'
PAIRS = {'BTCBRL', 'ETHBRL', 'SOLBRL'}
INTERVALS = {'1h': 3600000, '4h': 14400000, '1d': 86400000}
MAX_BYTES = 2_000_000


def _price(value):
    try:
        price = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError('INVALID_PRICE') from exc
    if not price.is_finite() or price <= 0:
        raise ValueError('INVALID_PRICE')
    return str(price)


def parse_klines(payload, *, symbol, interval='1h', now_ms=None):
    """Convert vendor reply into untrusted-for-trading BRL candles."""
    if symbol not in PAIRS or interval not in INTERVALS:
        raise ValueError('UNSUPPORTED_PAIR_OR_INTERVAL')
    if now_ms is None:
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    if not isinstance(payload, list) or not 1 <= len(payload) <= 500:
        raise ValueError('INVALID_PAYLOAD')
    bars = []
    previous_open = None
    for item in payload:
        if not isinstance(item, list) or len(item) < 7:
            raise ValueError('INVALID_KLINE')
        start, end = item[0], item[6]
        if (type(start) is not int or type(end) is not int or start < 0 or
                end != start + INTERVALS[interval] - 1 or
                (previous_open is not None and start <= previous_open)):
            raise ValueError('INVALID_KLINE_TIME')
        previous_open = start
        op, hi, lo, cl = (_price(item[i]) for i in range(1, 5))
        if Decimal(lo) > min(Decimal(op), Decimal(cl)) or Decimal(hi) < max(Decimal(op), Decimal(cl)):
            raise ValueError('INVALID_OHLC')
        if end >= now_ms:  # exclude incomplete current bar, even for a partial response
            continue
        bars.append({'at_utc': datetime.fromtimestamp(start / 1000, timezone.utc).isoformat(),
                     'open_brl': op, 'high_brl': hi, 'low_brl': lo, 'close_brl': cl,
                     'complete': True, 'verified': False})
    if not bars:
        raise ValueError('NO_COMPLETED_BARS')
    return {'market': 'CRYPTO', 'symbol': symbol, 'denomination': 'BRL',
            'bars': bars, 'bar_count': len(bars), 'venue': 'BINANCE_PUBLIC',
            'source': ENDPOINT, 'provenance_level': 'SINGLE_PUBLIC_EXCHANGE_RESPONSE',
            'independent_market_verification': False, 'usable_for_live_trading': False}


def fetch_public_candles(*, symbol='BTCBRL', interval='1h', limit=100, now_ms=None, opener=None):
    if symbol not in PAIRS or interval not in INTERVALS or type(limit) is not int or not 2 <= limit <= 500:
        raise ValueError('INVALID_REQUEST')
    url = f'{ENDPOINT}?symbol={symbol}&interval={interval}&limit={limit}'
    request = urllib.request.Request(url, headers={'User-Agent': 'TradingLabResearch/4.0', 'Accept': 'application/json'})
    opener = opener or urllib.request.urlopen
    with opener(request, timeout=10) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('RESPONSE_TOO_LARGE')
    try:
        payload = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise ValueError('INVALID_JSON') from exc
    result = parse_klines(payload, symbol=symbol, interval=interval, now_ms=now_ms)
    result['source_sha256'] = hashlib.sha256(raw).hexdigest()
    result['query_interval'] = interval
    return result


def main():
    parser = argparse.ArgumentParser(description='Fetch public BRL crypto candles; Shadow research only')
    parser.add_argument('--symbol', choices=sorted(PAIRS), default='BTCBRL')
    parser.add_argument('--interval', choices=sorted(INTERVALS), default='1h')
    parser.add_argument('--limit', type=int, default=100)
    args = parser.parse_args()
    try:
        result = fetch_public_candles(symbol=args.symbol, interval=args.interval, limit=args.limit)
        result['status'] = 'RESEARCH_ONLY'
        code = 0
    except Exception as exc:
        result = {'status': 'BLOCKED', 'reason': type(exc).__name__ + ': ' + str(exc),
                  'usable_for_live_trading': False}
        code = 2
    print(json.dumps(result, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
