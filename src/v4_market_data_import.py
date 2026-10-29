"""Read-only import of externally obtained OHLC candles for offline Shadow research.

A SHA-256 pin establishes byte-level integrity, NOT vendor authenticity or
market correctness. No network access and no automatic permission to trade.
"""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

MAX_BYTES = 12_000_000
MAX_ROWS = 100_000
MARKETS = {'B3_EQUITY', 'US_EQUITY', 'CRYPTO'}
FIELDS = ('at_utc', 'open_brl', 'high_brl', 'low_brl', 'close_brl')


def _decimal(s):
    if not isinstance(s, str) or not s.strip():
        raise ValueError('MISSING_PRICE')
    try:
        value = Decimal(s)
    except InvalidOperation as exc:
        raise ValueError('INVALID_PRICE') from exc
    if not value.is_finite() or value <= 0:
        raise ValueError('NONPOSITIVE_OR_NONFINITE_PRICE')
    return value


def load_pinned_csv(path, *, sha256, market, symbol, denomination='BRL'):
    """Validate file; return candles still untrusted for actual broker execution."""
    if market not in MARKETS or not isinstance(symbol, str) or not symbol.strip():
        raise ValueError('INVALID_MARKET_OR_SYMBOL')
    if denomination != 'BRL':
        raise ValueError('CURRENCY_CONVERSION_REQUIRED')
    if not isinstance(sha256, str) or len(sha256) != 64 or any(c not in '0123456789abcdef' for c in sha256):
        raise ValueError('INVALID_SHA256_PIN')
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('FILE_TOO_LARGE')
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != sha256:
        raise ValueError('SOURCE_HASH_MISMATCH')
    try:
        content = raw.decode('utf-8-sig')
    except UnicodeError as exc:
        raise ValueError('INVALID_ENCODING') from exc
    import io
    reader = csv.DictReader(io.StringIO(content), strict=True)
    if reader.fieldnames is None or set(reader.fieldnames) != set(FIELDS) or len(reader.fieldnames) != len(FIELDS):
        raise ValueError('INVALID_COLUMNS')
    bars = []
    previous = None
    for row in reader:
        if len(bars) >= MAX_ROWS or None in row or not all(isinstance(row[f], str) for f in FIELDS):
            raise ValueError('INVALID_OR_EXCESS_ROWS')
        try:
            timestamp = datetime.fromisoformat(row['at_utc'].replace('Z', '+00:00'))
        except (ValueError, TypeError) as exc:
            raise ValueError('INVALID_TIMESTAMP') from exc
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError('NAIVE_TIMESTAMP')
        timestamp = timestamp.astimezone(timezone.utc)
        if previous is not None and timestamp <= previous:
            raise ValueError('OUT_OF_ORDER_OR_DUPLICATE_TIMESTAMP')
        previous = timestamp
        op, hi, lo, cl = (_decimal(row[f]) for f in FIELDS[1:])
        if lo > op or op > hi or lo > cl or cl > hi:
            raise ValueError('INVALID_OHLC')
        bars.append({'at_utc': timestamp.isoformat(), 'open_brl': str(op), 'high_brl': str(hi),
                     'low_brl': str(lo), 'close_brl': str(cl), 'complete': True,
                     'verified': True})
    if not bars:
        raise ValueError('EMPTY_DATA')
    return {'market': market, 'symbol': symbol.strip().upper(), 'denomination': denomination,
            'source_sha256': actual, 'bar_count': len(bars), 'bars': bars,
            'provenance_level': 'LOCAL_SHA256_INTEGRITY_ONLY', 'independent_market_verification': False,
            'usable_for_live_trading': False}


def main():
    parser = argparse.ArgumentParser(description='Offline CSV candle validator; never authorizes trades')
    parser.add_argument('--file', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--market', required=True, choices=sorted(MARKETS))
    parser.add_argument('--symbol', required=True)
    args = parser.parse_args()
    try:
        result = load_pinned_csv(args.file, sha256=args.sha256, market=args.market, symbol=args.symbol)
        result.pop('bars')
        result['status'] = 'IMPORT_VALIDATED_OFFLINE_ONLY'
        code = 0
    except (ValueError, OSError, csv.Error) as exc:
        result = {'status': 'BLOCKED', 'reason': str(exc), 'usable_for_live_trading': False}
        code = 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
