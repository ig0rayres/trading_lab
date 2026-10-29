import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from v4_equity_feed import parse_chart, validate_symbol, fetch_public_candles
from v4_market_cycle import collect


def fixture(currency='BRL', symbol='ITUB4.SA', timestamps=None):
    return {'chart': {'error': None, 'result': [{'meta': {'currency': currency, 'symbol': symbol, 'instrumentType': 'EQUITY'},
        'timestamp': timestamps or [1700000000, 1700086400],
        'indicators': {'quote': [{'open': [10, 11], 'high': [12, 12], 'low': [9, 10], 'close': [11, 11]}]}}]}}


class TestEquityFeed(unittest.TestCase):
    def test_b3_currency(self):
        row = parse_chart(fixture(), market='B3_EQUITY', symbol='ITUB4', interval='1d', now_seconds=1700500000)
        self.assertEqual(row['denomination'], 'BRL')
        self.assertEqual(row['bar_count'], 2)
        self.assertFalse(row['usable_for_live_trading'])

    def test_us_currency(self):
        row = parse_chart(fixture('USD', 'AAPL'), market='US_EQUITY', symbol='AAPL', interval='1d', now_seconds=1700500000)
        self.assertEqual(row['denomination'], 'USD')

    def test_currency_mismatch(self):
        with self.assertRaisesRegex(ValueError, 'MISMATCH'):
            parse_chart(fixture('USD'), market='B3_EQUITY', symbol='ITUB4', interval='1d')

    def test_unsorted(self):
        with self.assertRaisesRegex(ValueError, 'UNSORTED'):
            parse_chart(fixture(timestamps=[1700086400, 1700000000]), market='B3_EQUITY', symbol='ITUB4', interval='1d')

    def test_current_day_excluded(self):
        row = parse_chart(fixture(), market='B3_EQUITY', symbol='ITUB4', interval='1d', now_seconds=1700086400)
        self.assertEqual(row['bar_count'], 1)

    def test_bad_symbol(self):
        for symbol in ('itub4', '../secret', 'ITUB4&interval=1m'):
            with self.assertRaises(ValueError):
                validate_symbol('B3_EQUITY', symbol)

    def test_no_completed_bars(self):
        with self.assertRaisesRegex(ValueError, 'NO_COMPLETED'):
            parse_chart(fixture(), market='B3_EQUITY', symbol='ITUB4', interval='1d', now_seconds=1700000000)

    def test_null_bar_skipped(self):
        payload = fixture()
        payload['chart']['result'][0]['indicators']['quote'][0]['close'][1] = None
        row = parse_chart(payload, market='B3_EQUITY', symbol='ITUB4', interval='1d', now_seconds=1700500000)
        self.assertEqual(row['bar_count'], 1)


class TestCycle(unittest.TestCase):
    def test_success(self):
        def equity(**kwargs):
            return {'market': kwargs['market'], 'symbol': kwargs['symbol'], 'usable_for_live_trading': False}
        def crypto(**kwargs):
            return {'market': 'CRYPTO', 'symbol': kwargs['symbol'], 'usable_for_live_trading': False}
        result = collect(equity_fetch=equity, crypto_fetch=crypto)
        self.assertEqual(len(result['results']), 3)
        self.assertFalse(result['automatic_order_submission'])

    def test_partial_failure(self):
        def fail(**kwargs):
            raise TimeoutError('network down')
        result = collect(equity_fetch=fail, crypto_fetch=fail)
        self.assertEqual(result['status'], 'PARTIAL_OR_BLOCKED')
        self.assertEqual(len(result['errors']), 3)

    def test_reject_feed_marked_live(self):
        result = collect([('CRYPTO', 'BTCBRL')], crypto_fetch=lambda **kw: {'market':'CRYPTO', 'symbol':'BTCBRL', 'usable_for_live_trading':True})
        self.assertEqual(len(result['errors']), 1)

    def test_duplicate(self):
        def equity(**kwargs):
            return {'market':kwargs['market'], 'symbol':kwargs['symbol'], 'usable_for_live_trading':False}
        result = collect([('US_EQUITY','AAPL'), ('US_EQUITY','AAPL')], equity_fetch=equity)
        self.assertIn('DUPLICATE_UNIVERSE_ENTRY', result['errors']['US_EQUITY:AAPL'])


if __name__ == '__main__':
    unittest.main()

class TestEquityTransport(unittest.TestCase):
    def test_public_request_and_hash(self):
        import io
        import json
        import hashlib
        raw = json.dumps(fixture('USD', 'AAPL')).encode()
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, size): return raw
        def opener(request, timeout):
            self.assertIn('AAPL?', request.full_url)
            self.assertIn('range=1mo', request.full_url)
            self.assertEqual(timeout, 10)
            return Response()
        row = fetch_public_candles(market='US_EQUITY', symbol='AAPL', now_seconds=1700500000, opener=opener)
        self.assertEqual(row['source_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertFalse(row['usable_for_live_trading'])

    def test_oversized_response(self):
        from v4_equity_feed import MAX_BYTES
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, size): return b'0' * (MAX_BYTES + 1)
        with self.assertRaisesRegex(ValueError, 'RESPONSE_TOO_LARGE'):
            fetch_public_candles(market='US_EQUITY', symbol='AAPL', opener=lambda *a, **kw: Response())
