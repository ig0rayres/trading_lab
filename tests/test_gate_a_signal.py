import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import gate_a_signal as ga


class GateAUnitTest(unittest.TestCase):
    def test_idempotency_stable(self):
        a = ga.idempotency_key('tradingview', 'SIG123456')
        b = ga.idempotency_key('tradingview', 'SIG123456')
        self.assertEqual(a, b)
        self.assertEqual(len(a), 64)


@unittest.skipUnless(os.environ.get('LEDGER_DATABASE_URL'), 'LEDGER_DATABASE_URL not set')
class GateAIntegrationTest(unittest.TestCase):
    def setUp(self):
        import ledger_migrate as lm

        lm.apply()

    def test_ingest_queues_and_persists_signal(self):
        import ledger_migrate as lm
        import ledger_store as store
        import tradingview_webhook as tv

        os.environ['SIGNAL_COPY_SECRET'] = 'x' * 48
        with __import__('tempfile').TemporaryDirectory() as d:
            payload = {
                'provider': 'tradingview',
                'signal_id': 'GATEA_TEST_001',
                'symbol': 'AAPL',
                'side': 'buy',
                'asset_class': 'us_equity',
                'sent_at_utc': datetime.now(timezone.utc).isoformat(),
                'entry': '150',
                'stop': '145',
                'target': '160',
                'quantity': 1,
                'ttl_seconds': 30,
            }
            status, body = tv.ingest(payload, 'a' * 48, Path(d) / 'pending')
            self.assertEqual(status, 202)
            self.assertEqual(body['orders_sent'], 0)
            with store.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT status FROM signal_events WHERE idempotency_key = %s",
                        (ga.idempotency_key('tradingview', 'GATEA_TEST_001'),),
                    )
                    row = cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 'accepted')


if __name__ == '__main__':
    unittest.main()
