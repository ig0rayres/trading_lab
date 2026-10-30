import os
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'src'))
from tradingview_webhook import ingest


def _weekday_open_utc():
    # Tuesday 2026-10-28 15:00 ET — inside regular session
    return datetime(2026, 10, 28, 19, 0, tzinfo=timezone.utc)


class TVTests(unittest.TestCase):
    def signal(self):
        return {
            'provider': 'tradingview',
            'signal_id': 'SAMPLE_123456',
            'symbol': 'AAPL',
            'side': 'buy',
            'asset_class': 'us_equity',
            'sent_at_utc': _weekday_open_utc().isoformat(),
            'entry': '150',
            'stop': '145',
            'target': '160',
            'quantity': 1,
            'ttl_seconds': 30,
        }

    def test_queue_and_dedupe(self):
        now = _weekday_open_utc()
        with tempfile.TemporaryDirectory() as d:
            os.environ['SIGNAL_COPY_SECRET'] = 'x' * 48
            a = ingest(self.signal(), 'a' * 48, pathlib.Path(d) / 'pending', now=now)
            b = ingest(self.signal(), 'a' * 48, pathlib.Path(d) / 'pending', now=now)
            self.assertEqual(a[0], 202)
            self.assertEqual(a[1].get('orders_sent'), 0)
            self.assertEqual(b[1]['status'], 'DUPLICATE_IGNORED')

    def test_invalid_direction(self):
        s = self.signal()
        s['side'] = 'sell'
        with tempfile.TemporaryDirectory() as d:
            status, body = ingest(s, 'a' * 48, pathlib.Path(d), now=_weekday_open_utc())
            self.assertEqual(status, 422)
            self.assertEqual(body['reason'], 'UNSUPPORTED_ASSET_OR_SIDE')
            self.assertNotIn('orders_sent', body)

    def test_invalid_timestamp(self):
        s = self.signal()
        s['sent_at_utc'] = '2020-01-01T00:00:00+00:00'
        with tempfile.TemporaryDirectory() as d:
            status, body = ingest(s, 'a' * 48, pathlib.Path(d), now=_weekday_open_utc())
            self.assertEqual(status, 422)
            self.assertEqual(body['reason'], 'STALE_OR_INVALID_TIMESTAMP')

    def test_invalid_fields(self):
        with tempfile.TemporaryDirectory() as d:
            status, body = ingest({'provider': 'tradingview'}, 'a' * 48, pathlib.Path(d), now=_weekday_open_utc())
            self.assertEqual(status, 422)
            self.assertEqual(body['reason'], 'INVALID_FIELDS')

    def test_outside_session_weekend(self):
        saturday = datetime(2026, 11, 1, 15, 0, tzinfo=timezone.utc)
        s = self.signal()
        s['sent_at_utc'] = saturday.isoformat()
        with tempfile.TemporaryDirectory() as d:
            status, body = ingest(s, 'a' * 48, pathlib.Path(d), now=saturday)
            self.assertEqual(status, 422)
            self.assertEqual(body['reason'], 'OUTSIDE_SESSION')


if __name__ == '__main__':
    unittest.main()
