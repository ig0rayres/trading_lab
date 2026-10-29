"""Read-only public Yahoo chart collector for US and B3 research.

No guarantee of provider availability, exchange licensing, or independent price
verification. Never usable by an execution adapter without separate validation.
"""
import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

ENDPOINT = 'https://query1.finance.yahoo.com/v8/finance/chart/'
MAX_BYTES = 3_000_000
INTERVALS = {'1d', '1h'}
RANGES = {'5d', '1mo', '3mo'}
US_SYMBOL = re.compile(r'^[A-Z][A-Z0-9.]{0,9}$')
B3_SYMBOL = re.compile(r'^[A-Z]{4}[0-9]{1,2}$')


def _price(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError('INVALID_PRICE') from exc
    if not result.is_finite() or result <= 0:
        raise ValueError('INVALID_PRICE')
    return str(result)


def validate_symbol(market, symbol):
    if not isinstance(symbol, str) or symbol != symbol.upper():
        raise ValueError('INVALID_SYMBOL')
    if market == 'B3_EQUITY' and B3_SYMBOL.fullmatch(symbol):
        return symbol + '.SA', 'BRL'
    if market == 'US_EQUITY' and US_SYMBOL.fullmatch(symbol):
        return symbol, 'USD'
    raise ValueError('INVALID_MARKET_OR_SYMBOL')


def parse_chart(payload, *, market, symbol, interval, now_seconds=None):
    query_symbol, currency = validate_symbol(market, symbol)
    if interval not in INTERVALS or not isinstance(payload, dict):
        raise ValueError('INVALID_RESPONSE')
    try:
        chart = payload['chart']
        if chart.get('error') is not None:
            raise ValueError('PROVIDER_ERROR')
        results = chart['result']
        if not isinstance(results, list) or len(results) != 1:
            raise ValueError('INVALID_RESULTS')
        result = results[0]
        meta = result['meta']
        timestamps = result['timestamp']
        quote = result['indicators']['quote'][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError('INVALID_RESPONSE_SHAPE') from exc
    if meta.get('currency') != currency or meta.get('symbol', '').upper() != query_symbol:
        raise ValueError('SYMBOL_OR_CURRENCY_MISMATCH')
    if meta.get('instrumentType') not in ('EQUITY', 'ETF'):
        raise ValueError('UNSUPPORTED_INSTRUMENT')
    if not isinstance(timestamps, list) or not 1 <= len(timestamps) <= 2000:
        raise ValueError('INVALID_TIMESTAMPS')
    if not all(isinstance(quote.get(k), list) and len(quote[k]) == len(timestamps) for k in ('open', 'high', 'low', 'close')):
        raise ValueError('INVALID_PRICE_ARRAYS')
    now_seconds = now_seconds if now_seconds is not None else int(datetime.now(timezone.utc).timestamp())
    if type(now_seconds) is not int:
        raise ValueError('INVALID_CLOCK')
    period = 86400 if interval == '1d' else 3600
    bars = []
    previous = -1
    for idx, ts in enumerate(timestamps):
        if type(ts) is not int or ts <= previous or ts < 0:
            raise ValueError('UNSORTED_TIMESTAMP')
        previous = ts
        prices = [quote[k][idx] for k in ('open', 'high', 'low', 'close')]
        if any(p is None for p in prices):
            continue  # explicit vendor missing bar, not a fabricated price
        op, hi, lo, cl = map(_price, prices)
        if Decimal(lo) > min(Decimal(op), Decimal(cl)) or Decimal(hi) < max(Decimal(op), Decimal(cl)):
            raise ValueError('INVALID_OHLC')
        # Conservative daily completion: do not include today's daily bar.
        dt = datetime.fromtimestamp(ts, timezone.utc)
        now_dt = datetime.fromtimestamp(now_seconds, timezone.utc)
        if interval == '1d' and dt.date() >= now_dt.date():
            continue
        if interval == '1h' and ts + period > now_seconds:
            continue
        bars.append({'at_utc': dt.isoformat(), 'open': op, 'high': hi,
                     'low': lo, 'close': cl, 'complete': True, 'verified': False})
    if not bars:
        raise ValueError('NO_COMPLETED_BARS')
    return {'market': market, 'symbol': symbol, 'denomination': currency,
            'bars': bars, 'bar_count': len(bars), 'venue': 'YAHOO_PUBLIC_CHART',
            'source': ENDPOINT, 'provenance_level': 'SINGLE_PUBLIC_DATA_PROVIDER',
            'independent_market_verification': False, 'usable_for_live_trading': False}


def fetch_public_candles(*, market, symbol, interval='1d', period='1mo', now_seconds=None, opener=None):
    provider_symbol, _ = validate_symbol(market, symbol)
    if interval not in INTERVALS or period not in RANGES:
        raise ValueError('INVALID_REQUEST')
    url = ENDPOINT + urllib.parse.quote(provider_symbol, safe='.') + '?' + urllib.parse.urlencode({'interval': interval, 'range': period})
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
    result = parse_chart(payload, market=market, symbol=symbol, interval=interval, now_seconds=now_seconds)
    result['source_sha256'] = hashlib.sha256(raw).hexdigest()
    result['query_interval'] = interval
    return result


def main():
    parser = argparse.ArgumentParser(description='Read-only public chart collector, Shadow only')
    parser.add_argument('--market', choices=['US_EQUITY', 'B3_EQUITY'], required=True)
    parser.add_argument('--symbol', required=True)
    parser.add_argument('--interval', choices=sorted(INTERVALS), default='1d')
    parser.add_argument('--period', choices=sorted(RANGES), default='1mo')
    args = parser.parse_args()
    try:
        result = fetch_public_candles(market=args.market, symbol=args.symbol, interval=args.interval, period=args.period)
        result['status'] = 'RESEARCH_ONLY'
        status = 0
    except Exception as exc:
        result = {'status': 'BLOCKED', 'reason': str(exc), 'usable_for_live_trading': False}
        status = 2
    print(json.dumps(result, indent=2))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
