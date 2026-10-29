import json
import pytest
from v4_crypto_feed import fetch_public_candles, parse_klines

HOUR = 3600000

def bar(start, o='100', h='110', l='90', c='105'):
    return [start, o, h, l, c, '10', start + HOUR - 1]


def test_excludes_partial_and_preserves_brl():
    result = parse_klines([bar(0), bar(HOUR)], symbol='BTCBRL', now_ms=HOUR * 2 - 100)
    assert len(result['bars']) == 1
    assert result['bars'][0]['close_brl'] == '105'
    assert result['bars'][0]['verified'] is False
    assert result['usable_for_live_trading'] is False


def test_rejects_unsorted_and_malformed():
    with pytest.raises(ValueError, match='INVALID_KLINE_TIME'):
        parse_klines([bar(HOUR), bar(0)], symbol='BTCBRL', now_ms=3*HOUR)
    with pytest.raises(ValueError, match='INVALID_OHLC'):
        parse_klines([bar(0, h='95')], symbol='BTCBRL', now_ms=3*HOUR)
    with pytest.raises(ValueError, match='INVALID_PRICE'):
        parse_klines([bar(0, c='NaN')], symbol='BTCBRL', now_ms=3*HOUR)


def test_all_partial_blocks():
    with pytest.raises(ValueError, match='NO_COMPLETED_BARS'):
        parse_klines([bar(HOUR)], symbol='BTCBRL', now_ms=HOUR+1)


def test_unknown_asset_blocks():
    with pytest.raises(ValueError, match='UNSUPPORTED_PAIR'):
        parse_klines([bar(0)], symbol='DOGEBRL')


class Response:
    def __init__(self, data): self.data = data
    def __enter__(self): return self
    def __exit__(self, *_): pass
    def read(self, amount): return self.data[:amount]


def test_fetch_without_network():
    def opener(request, timeout):
        assert 'symbol=BTCBRL' in request.full_url
        assert timeout == 10
        return Response(json.dumps([bar(0)]).encode())
    result = fetch_public_candles(now_ms=3*HOUR, opener=opener)
    assert result['bar_count'] == 1
    assert len(result['source_sha256']) == 64


def test_too_large_response():
    def opener(request, timeout): return Response(b'x' * 2_000_010)
    with pytest.raises(ValueError, match='RESPONSE_TOO_LARGE'):
        fetch_public_candles(opener=opener)


def test_api_error_fails_closed():
    def opener(request, timeout): return Response(b'{"code":-1003,"msg":"rate limit"}')
    with pytest.raises(ValueError, match='INVALID_PAYLOAD'):
        fetch_public_candles(opener=opener)


def test_request_limits():
    with pytest.raises(ValueError, match='INVALID_REQUEST'):
        fetch_public_candles(limit=1000)
