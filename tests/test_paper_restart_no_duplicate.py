"""N21.3 — service restart resumes tracking without a second broker submission."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import paper_gateway_queue as pgq


@unittest.skipUnless(os.environ.get('LEDGER_DATABASE_URL'), 'LEDGER_DATABASE_URL not set')
class PaperRestartNoDuplicateTest(unittest.TestCase):
    def setUp(self):
        import ledger_migrate as lm

        lm.apply()

    def test_same_intent_after_restart_tracks_without_second_broker_call(self):
        import ledger_store as store
        from gate_a_signal import idempotency_key, record_signal_event
        from ledger_store import insert_row

        signal = {
            'provider': 'tradingview',
            'signal_id': 'N21_RESTART_INTENT',
            'symbol': 'AAPL',
            'side': 'buy',
            'asset_class': 'us_equity',
            'entry': '100',
            'stop': '99',
            'target': '102',
            'quantity': 1,
            'strategy_key': 'signal_copy',
        }
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        env = {
            'LIVE_TRADING_ENABLED': 'false',
            'PAPER_SIGNAL_AUTO_ENABLED': 'true',
            'PAPER_EXECUTION_ENABLED': 'true',
            'PAPER_SIGNAL_ACCOUNT_ACK': 'I_AUTHORIZE_ALPACA_PAPER_ONLY',
        }
        queued = pgq.queue_intent(signal, decision)
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=signal,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            conn.commit()
        pgq.persist_intent(signal, decision, queued)
        broker_id = 'alpaca-broker-n21-restart'
        client_order_id = queued['client_order_id']
        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE paper_orders SET broker_order_id = %s, status = %s '
                    'WHERE client_order_id = %s',
                    (broker_id, 'submitted', client_order_id),
                )
            conn.commit()

        broker_calls = []
        track_calls = []

        def fake_broker_run(sig, e, ledger=None, **kwargs):
            broker_calls.append(sig['signal_id'])
            return {
                'status': 'PAPER_SUBMITTED',
                'orders_sent': 1,
                'client_order_id': client_order_id,
                'broker_id': broker_id,
            }

        def fake_track(order, e, **kwargs):
            track_calls.append(order['client_order_id'])
            return {
                'status': 'TRACKED_FILLED',
                'terminal': True,
                'treated_as_fill': False,
                'orders_sent': 0,
            }

        with patch.object(pgq, 'paper_run', side_effect=fake_broker_run):
            first = pgq.process_after_gate_b(signal, decision, env, track_fn=fake_track)
        self.assertEqual(first['mode'], 'RESUMED_AFTER_RESTART')
        self.assertEqual(first['orders_sent'], 0)
        self.assertEqual(broker_calls, [])
        self.assertEqual(track_calls, [client_order_id])

        with patch.object(pgq, 'paper_run', side_effect=fake_broker_run) as broker:
            second = pgq.process_after_gate_b(signal, decision, env, track_fn=fake_track)
        broker.assert_not_called()
        self.assertEqual(second['mode'], 'RESUMED_AFTER_RESTART')
        self.assertEqual(second['orders_sent'], 0)
        self.assertEqual(len(broker_calls), 0)
        self.assertEqual(len(track_calls), 2)

        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT COUNT(*) FROM paper_orders po '
                    'JOIN risk_decisions rd ON rd.id = po.risk_decision_id '
                    'JOIN signal_events se ON se.id = rd.signal_event_id '
                    'WHERE se.idempotency_key = %s',
                    (idempotency_key('tradingview', 'N21_RESTART_INTENT'),),
                )
                count = cur.fetchone()[0]
        self.assertEqual(count, 1)


if __name__ == '__main__':
    unittest.main()
