import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import gate_a_signal as ga
import tradingview_webhook as tv


def _weekday_open_utc():
    return datetime(2026, 10, 28, 19, 0, tzinfo=timezone.utc)


def _valid_payload():
    now = _weekday_open_utc()
    return {
        'provider': 'tradingview',
        'signal_id': 'HTTP_TEST_123456',
        'symbol': 'AAPL',
        'side': 'buy',
        'asset_class': 'us_equity',
        'sent_at_utc': now.isoformat(),
        'entry': '150',
        'stop': '145',
        'target': '160',
        'quantity': 1,
        'ttl_seconds': 30,
    }


class WebhookHttpDispatchTest(unittest.TestCase):
    def setUp(self):
        self.token = 'a' * 48
        self.env = {
            'TV_WEBHOOK_TOKEN': self.token,
            'SIGNAL_COPY_SECRET': 'x' * 48,
            'LIVE_TRADING_ENABLED': 'false',
        }

    def test_spec_path_requires_header_401(self):
        body = json.dumps(_valid_payload()).encode()
        with patch.dict(os.environ, self.env, clear=False):
            status, resp = tv.dispatch_post(
                '/webhooks/tradingview',
                {'Content-Type': 'application/json'},
                body,
            )
        self.assertEqual(status, 401)
        self.assertEqual(resp['status'], 'UNAUTHORIZED')

    def test_spec_path_accepts_header(self):
        body = json.dumps(_valid_payload()).encode()
        now = _weekday_open_utc()
        with patch.dict(os.environ, self.env, clear=False):
            with tempfile.TemporaryDirectory() as d:
                with mock.patch.object(tv, 'QUEUE', Path(d) / 'pending'):
                    status, resp = tv.dispatch_post(
                        '/webhooks/tradingview',
                        {
                            'Content-Type': 'application/json',
                            'X-Webhook-Token': self.token,
                        },
                        body,
                        now=now,
                        queue=Path(d) / 'pending',
                    )
        self.assertEqual(status, 202)
        self.assertEqual(resp.get('orders_sent'), 0)

    def test_legacy_path_token_in_url(self):
        body = json.dumps(_valid_payload()).encode()
        now = _weekday_open_utc()
        with patch.dict(os.environ, self.env, clear=False):
            with tempfile.TemporaryDirectory() as d:
                with mock.patch.object(tv, 'QUEUE', Path(d) / 'pending'):
                    status, resp = tv.dispatch_post(
                        '/webhook/' + self.token,
                        {'Content-Type': 'application/json'},
                        body,
                        now=now,
                        queue=Path(d) / 'pending',
                    )
        self.assertEqual(status, 202)

    def test_legacy_bad_token_404(self):
        with patch.dict(os.environ, self.env, clear=False):
            status, resp = tv.dispatch_post(
                '/webhook/' + ('b' * 48),
                {'Content-Type': 'application/json'},
                json.dumps(_valid_payload()).encode(),
            )
        self.assertEqual(status, 404)


@unittest.skipUnless(os.environ.get('LEDGER_DATABASE_URL'), 'LEDGER_DATABASE_URL not set')
class GateANewsLedgerTest(unittest.TestCase):
    def setUp(self):
        import ledger_migrate as lm

        lm.apply()

    def test_news_first_report_audited(self):
        report = {
            'mode': 'NEWS_FIRST_INTERNAL_SIMULATION',
            'signals': [
                {
                    'id': 'newsaudit001',
                    'symbol': 'AAPL',
                    'decision': 'NO_TRADE',
                    'blocker_reasons': ['EVIDENCE_PENDING'],
                }
            ],
        }
        n = ga.persist_news_first_report(report)
        self.assertEqual(n, 1)
        import ledger_store as store

        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT status, reject_code, source FROM signal_events WHERE idempotency_key = %s',
                    (ga.idempotency_key('news_first', 'newsaudit001'),),
                )
                row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'rejected')
        self.assertEqual(row[1], 'EVIDENCE_PENDING')
        self.assertEqual(row[2], 'news_first')


if __name__ == '__main__':
    unittest.main()
