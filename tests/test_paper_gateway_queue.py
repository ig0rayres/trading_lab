import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import paper_gateway_queue as pgq


def _signal():
    return {
        'provider': 'tradingview',
        'signal_id': 'QUEUE_TEST_001',
        'symbol': 'AAPL',
        'side': 'buy',
        'asset_class': 'us_equity',
        'entry': '100',
        'stop': '99',
        'target': '102',
        'quantity': 1,
    }


class PaperGatewayQueueTest(unittest.TestCase):
    def test_queue_never_calls_broker(self):
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        env = {'LIVE_TRADING_ENABLED': 'false', 'PAPER_SIGNAL_AUTO_ENABLED': 'false'}
        with patch.object(pgq, 'paper_run') as broker:
            out = pgq.process_after_gate_b(_signal(), decision, env, broker_run=broker)
        broker.assert_not_called()
        self.assertEqual(out['status'], 'QUEUED')
        self.assertEqual(out['mode'], 'PAPER_GATEWAY_QUEUE_ONLY')
        self.assertEqual(out['orders_sent'], 0)
        self.assertIn('client_order_id', out)

    def test_rejected_gate_b_no_queue(self):
        decision = {'decision': 'rejected', 'reject_code': 'LOSS'}
        out = pgq.process_after_gate_b(_signal(), decision, {})
        self.assertEqual(out['status'], 'BLOCKED')
        self.assertEqual(out['orders_sent'], 0)


@unittest.skipUnless(os.environ.get('LEDGER_DATABASE_URL'), 'LEDGER_DATABASE_URL not set')
class GateBLedgerIntegrationTest(unittest.TestCase):
    def setUp(self):
        import ledger_migrate as lm

        lm.apply()

    def test_intent_persists_paper_order(self):
        import ledger_store as store
        from gate_a_signal import record_signal_event, idempotency_key
        from paper_gateway_queue import persist_intent, queue_intent

        signal = _signal()
        signal['provider'] = 'tradingview'
        signal['signal_id'] = 'LEDGER_B_001'
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        queued = queue_intent(signal, decision)
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=signal,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            conn.commit()
        persist_intent(signal, decision, queued)
        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT po.status FROM paper_orders po "
                    "JOIN risk_decisions rd ON rd.id = po.risk_decision_id "
                    "JOIN signal_events se ON se.id = rd.signal_event_id "
                    'WHERE se.idempotency_key = %s',
                    (idempotency_key('tradingview', 'LEDGER_B_001'),),
                )
                row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'queued_intent')

    def test_reject_persists_risk_decision(self):
        import ledger_store as store
        from gate_a_signal import idempotency_key, record_signal_event

        signal = _signal()
        signal['signal_id'] = 'GATEB_REJ_001'
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=signal,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            conn.commit()
        decision = {'decision': 'rejected', 'reject_code': 'LOSS', 'risk_amount_cents': 0}
        pgq.persist_risk_decision(signal, decision)
        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT rd.decision, rd.reject_code FROM risk_decisions rd "
                    "JOIN signal_events se ON se.id = rd.signal_event_id "
                    'WHERE se.idempotency_key = %s',
                    (idempotency_key('tradingview', 'GATEB_REJ_001'),),
                )
                row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'rejected')
        self.assertEqual(row[1], 'LOSS')


if __name__ == '__main__':
    unittest.main()
