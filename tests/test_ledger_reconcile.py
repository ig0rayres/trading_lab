import os
import sys
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import ledger_reconcile as lr


@unittest.skipUnless(os.environ.get('LEDGER_DATABASE_URL'), 'LEDGER_DATABASE_URL not set')
class LedgerReconcileTest(unittest.TestCase):
    def setUp(self):
        import ledger_migrate as lm

        lm.apply()

    def test_apply_links_activity_to_paper_order(self):
        import ledger_store as store
        from gate_a_signal import record_signal_event
        from ledger_store import insert_row

        signal = {
            'provider': 'tradingview',
            'signal_id': 'RECON_001',
            'symbol': 'AAPL',
            'side': 'buy',
        }
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=signal,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            from gate_a_signal import idempotency_key

            with conn.cursor() as cur:
                cur.execute(
                    'SELECT id FROM signal_events WHERE idempotency_key = %s',
                    (idempotency_key('tradingview', 'RECON_001'),),
                )
                se_id = cur.fetchone()[0]
            risk_id = uuid.uuid4()
            insert_row(
                conn,
                'risk_decisions',
                {
                    'id': risk_id,
                    'signal_event_id': se_id,
                    'strategy_key': 'signal_copy',
                    'decision': 'paper_allowed',
                    'reject_code': None,
                    'risk_amount_cents': 500,
                },
            )
            insert_row(
                conn,
                'paper_orders',
                {
                    'risk_decision_id': risk_id,
                    'position_id': None,
                    'client_order_id': 'nf-recon-test',
                    'broker_order_id': None,
                    'symbol': 'AAPL',
                    'side': 'long',
                    'status': 'queued_intent',
                    'qty': 1,
                },
            )
            conn.commit()
        report = {
            'mode': 'READ_ONLY',
            'activities': {
                'activities': [
                    {'id': 'alpaca-fill-001', 'symbol': 'AAPL', 'side': 'buy', 'qty': '1', 'price': '100.00'},
                ],
            },
        }
        out = lr.apply_from_report(report)
        self.assertEqual(out['status'], 'APPLIED_READ_ONLY')
        self.assertEqual(out['linked'], 1)
        self.assertEqual(out['orders_sent'], 0)
        snap = lr.ledger_snapshot()
        self.assertGreaterEqual(snap.get('paper_fills', 0), 1)


if __name__ == '__main__':
    unittest.main()
