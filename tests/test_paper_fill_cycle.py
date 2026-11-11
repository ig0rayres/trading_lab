"""N21.1 — track submitted paper order to terminal state (ADR-007, Feature 7)."""
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import paper_fill_cycle as pfc


def _env():
    return {
        'LIVE_TRADING_ENABLED': 'false',
        'ALPACA_PAPER_TRADE': 'true',
        'ALPACA_BASE_URL': 'https://paper-api.alpaca.markets',
        'ALPACA_API_KEY': 'test',
        'ALPACA_SECRET_KEY': 'test',
        'USD_BRL_REFERENCE': '5',
    }


def _open_order(**kw):
    base = {
        'client_order_id': 'nf-' + 'a' * 24,
        'broker_order_id': 'alpaca-order-n21',
        'status': 'accepted',
        'symbol': 'AAPL',
        'side': 'long',
        'qty': 1,
        'market': 'us_equity',
        'idempotency_key': 'tradingview:FILL_CYCLE_001',
        'ttl_seconds': 60,
        'submitted_at_utc': '2026-11-11T15:00:00+00:00',
    }
    base.update(kw)
    return base


class PaperFillCycleTests(unittest.TestCase):
    def test_filled_applies_ledger_read_only(self):
        applied = []

        def reconcile(cid, env, opener=None):
            self.assertEqual(cid, _open_order()['client_order_id'])
            return {
                'status': 'RECONCILED',
                'orders_sent': 0,
                'broker_status': 'filled',
                'filled_qty': '1',
                'filled_avg_price': '349.85',
                'id': _open_order()['broker_order_id'],
                'client_order_id': cid,
                'symbol': 'AAPL',
                'side': 'buy',
            }

        def ledger_apply(report):
            applied.append(report)
            return {'status': 'APPLIED_READ_ONLY', 'linked': 1, 'orders_sent': 0}

        out = pfc.track_once(
            _open_order(),
            _env(),
            reconcile_fn=reconcile,
            ledger_apply_fn=ledger_apply,
        )
        self.assertEqual(out['status'], 'TRACKED_FILLED')
        self.assertEqual(out['orders_sent'], 0)
        self.assertTrue(out.get('terminal'))
        self.assertEqual(len(applied), 1)
        self.assertEqual(applied[0].get('mode'), 'READ_ONLY')

    def test_canceled_terminal_without_fill(self):
        def reconcile(cid, env, opener=None):
            return {
                'status': 'RECONCILED',
                'orders_sent': 0,
                'broker_status': 'canceled',
                'id': _open_order()['broker_order_id'],
                'client_order_id': cid,
            }

        def forbid_apply(_report):
            raise AssertionError('ledger apply must not run without fill')

        out = pfc.track_once(
            _open_order(),
            _env(),
            reconcile_fn=reconcile,
            ledger_apply_fn=forbid_apply,
        )
        self.assertEqual(out['status'], 'TRACKED_CANCELED')
        self.assertEqual(out['orders_sent'], 0)
        self.assertTrue(out.get('terminal'))
        self.assertFalse(out.get('treated_as_fill'))

    def test_expired_terminal_recorded(self):
        def reconcile(cid, env, opener=None):
            return {
                'status': 'RECONCILED',
                'orders_sent': 0,
                'broker_status': 'expired',
                'client_order_id': cid,
            }

        out = pfc.track_once(_open_order(), _env(), reconcile_fn=reconcile)
        self.assertEqual(out['status'], 'TRACKED_EXPIRED')
        self.assertTrue(out.get('terminal'))
        self.assertFalse(out.get('treated_as_fill'))

    def test_ttl_without_fill_cancels_and_blocks_auto_resubmit(self):
        cid = _open_order()['client_order_id']
        canceled = []

        def reconcile(_cid, env, opener=None):
            return {
                'status': 'RECONCILED',
                'orders_sent': 0,
                'broker_status': 'new',
                'client_order_id': cid,
            }

        def cancel_fn(broker_order_id, env):
            canceled.append(broker_order_id)
            return {'status': 'CANCEL_ACCEPTED', 'orders_sent': 0}

        order = _open_order()
        out = pfc.track_once(
            order,
            _env(),
            now_utc='2026-11-11T15:02:00+00:00',
            reconcile_fn=reconcile,
            cancel_fn=cancel_fn,
        )
        self.assertEqual(canceled, [order['broker_order_id']])
        self.assertEqual(out['status'], 'TRACKED_CANCELLED_TTL')
        self.assertEqual(out['orders_sent'], 0)
        self.assertTrue(out.get('terminal'))
        self.assertFalse(out.get('treated_as_fill'))
        self.assertFalse(pfc.may_auto_resubmit(order, _env()))

    def test_live_trading_forbidden(self):
        env = dict(_env(), LIVE_TRADING_ENABLED='true')
        with self.assertRaisesRegex(ValueError, 'LIVE_TRADING_FORBIDDEN'):
            pfc.track_once(_open_order(), env)

    def test_shadow_local_market_never_treated_as_fill(self):
        def reconcile(cid, env, opener=None):
            return {
                'status': 'RECONCILED',
                'orders_sent': 0,
                'broker_status': 'filled',
                'client_order_id': cid,
                'source': 'LOCAL_SHADOW_BROKER',
            }

        def forbid_apply(_report):
            raise AssertionError('shadow path must not append paper_fills')

        order = _open_order(market='B3_EQUITY', broker_source='shadow')
        out = pfc.track_once(
            order,
            _env(),
            reconcile_fn=reconcile,
            ledger_apply_fn=forbid_apply,
        )
        self.assertNotEqual(out.get('status'), 'TRACKED_FILLED')
        self.assertEqual(out['orders_sent'], 0)
        self.assertFalse(out.get('treated_as_fill'))

    def test_unknown_broker_state_not_marked_executed(self):
        def reconcile(_cid, env, opener=None):
            return {'status': 'UNKNOWN_BROKER_STATE', 'orders_sent': 0}

        out = pfc.track_once(_open_order(), _env(), reconcile_fn=reconcile)
        self.assertEqual(out['status'], 'UNKNOWN_BROKER_STATE')
        self.assertFalse(out.get('terminal'))
        self.assertFalse(out.get('treated_as_fill'))


@unittest.skipUnless(os.environ.get('LEDGER_DATABASE_URL'), 'LEDGER_DATABASE_URL not set')
class PaperFillCycleLedgerIntegration(unittest.TestCase):
    def setUp(self):
        import ledger_migrate as lm

        lm.apply()

    def test_filled_cycle_persists_paper_fill_row(self):
        import ledger_reconcile as lr
        import ledger_store as store
        from gate_a_signal import idempotency_key, record_signal_event
        from ledger_store import insert_row
        import uuid

        signal = {
            'provider': 'tradingview',
            'signal_id': 'N21_FILL_CYCLE_INT',
            'symbol': 'AAPL',
            'side': 'buy',
        }
        client_order_id = 'nf-' + 'b' * 24
        broker_order_id = 'alpaca-int-n21'
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=signal,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT id FROM signal_events WHERE idempotency_key = %s',
                    (idempotency_key('tradingview', 'N21_FILL_CYCLE_INT'),),
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
                    'client_order_id': client_order_id,
                    'broker_order_id': broker_order_id,
                    'symbol': 'AAPL',
                    'side': 'long',
                    'status': 'accepted',
                    'qty': 1,
                },
            )
            conn.commit()

        def reconcile(cid, env, opener=None):
            self.assertEqual(cid, client_order_id)
            return {
                'status': 'RECONCILED',
                'orders_sent': 0,
                'broker_status': 'filled',
                'filled_qty': '1',
                'filled_avg_price': '100.00',
                'id': broker_order_id,
                'client_order_id': cid,
                'symbol': 'AAPL',
                'side': 'buy',
            }

        def ledger_apply(report):
            return lr.apply_from_report(report)

        open_order = {
            'client_order_id': client_order_id,
            'broker_order_id': broker_order_id,
            'status': 'accepted',
            'symbol': 'AAPL',
            'side': 'long',
            'qty': 1,
            'market': 'us_equity',
            'idempotency_key': idempotency_key('tradingview', 'N21_FILL_CYCLE_INT'),
            'ttl_seconds': 60,
            'submitted_at_utc': '2026-11-11T15:00:00+00:00',
        }
        out = pfc.track_once(
            open_order,
            _env(),
            reconcile_fn=reconcile,
            ledger_apply_fn=ledger_apply,
        )
        self.assertEqual(out['status'], 'TRACKED_FILLED')
        snap = lr.ledger_snapshot()
        self.assertGreaterEqual(snap.get('paper_fills', 0), 1)


if __name__ == '__main__':
    unittest.main()
