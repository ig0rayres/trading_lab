"""N21.2 — daily/weekly loss anchor from ledger fills in BRL only."""
import os
import sys
import unittest
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import ledger_loss_anchor as la


class LossAnchorPureTest(unittest.TestCase):
    def test_empty_anchor_verified_zero(self):
        now = datetime(2026, 11, 11, 15, 0, tzinfo=timezone.utc)
        state = la.build_anchor_state([], [], now_utc=now)
        self.assertTrue(state['daily_pnl_verified'])
        self.assertTrue(state['weekly_pnl_verified'])
        self.assertEqual(state['daily_pnl_brl'], '0')
        self.assertEqual(state['weekly_pnl_brl'], '0')
        self.assertFalse(state['blocks_new_order'])

    def test_brl_amounts_sum_in_day_and_week(self):
        now = datetime(2026, 11, 11, 15, 0, tzinfo=timezone.utc)
        rows = [
            {'amount_cents': -3000, 'created_at': datetime(2026, 11, 11, 14, 0, tzinfo=timezone.utc)},
            {'amount_cents': -2000, 'created_at': datetime(2026, 11, 10, 14, 0, tzinfo=timezone.utc)},
        ]
        state = la.build_anchor_state(rows, [], now_utc=now)
        self.assertEqual(state['daily_pnl_brl'], '-30')
        self.assertEqual(state['weekly_pnl_brl'], '-50')
        self.assertTrue(state['daily_pnl_verified'])
        self.assertFalse(state['blocks_new_order'])

    def test_unconverted_fill_blocks_gate(self):
        now = datetime(2026, 11, 11, 15, 0, tzinfo=timezone.utc)
        pending = [{'paper_fill_id': 'x', 'quote_currency': 'USD'}]
        state = la.build_anchor_state([], pending, now_utc=now)
        self.assertTrue(state['blocks_new_order'])
        self.assertEqual(state['reject_code'], 'UNCONVERTED_FILL')


@unittest.skipUnless(os.environ.get('LEDGER_DATABASE_URL'), 'LEDGER_DATABASE_URL not set')
class LossAnchorLedgerIntegration(unittest.TestCase):
    def setUp(self):
        import ledger_migrate as lm

        lm.apply()
        self._clear_fill_ledger()

    def _clear_fill_ledger(self):
        import ledger_store as store

        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM ledger_entries')
                cur.execute('DELETE FROM paper_fills')
                cur.execute('DELETE FROM paper_orders')
                cur.execute('DELETE FROM risk_decisions')
                cur.execute('DELETE FROM signal_events')
            conn.commit()

    def _seed_order(self, symbol: str, client_order_id: str):
        import ledger_store as store
        from gate_a_signal import idempotency_key, record_signal_event
        from ledger_store import insert_row

        signal = {
            'provider': 'tradingview',
            'signal_id': client_order_id,
            'symbol': symbol,
            'side': 'buy',
        }
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
                    (idempotency_key('tradingview', client_order_id),),
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
            po_id = uuid.uuid4()
            insert_row(
                conn,
                'paper_orders',
                {
                    'id': po_id,
                    'risk_decision_id': risk_id,
                    'position_id': None,
                    'client_order_id': client_order_id,
                    'broker_order_id': 'broker-' + client_order_id[:8],
                    'symbol': symbol,
                    'side': 'long',
                    'status': 'filled',
                    'qty': 1,
                },
            )
            conn.commit()
        return po_id

    def _insert_brl_fill(self, paper_order_id, fill_id: str, amount_cents: int):
        import ledger_store as store
        from ledger_store import insert_row

        pf_id = uuid.uuid4()
        with store.connect() as conn:
            insert_row(
                conn,
                'paper_fills',
                {
                    'id': pf_id,
                    'paper_order_id': paper_order_id,
                    'broker_fill_id': fill_id,
                    'qty': 1,
                    'price_cents': 10000,
                    'quote_currency': 'BRL',
                },
            )
            insert_row(
                conn,
                'ledger_entries',
                {
                    'paper_fill_id': pf_id,
                    'amount_cents': amount_cents,
                    'kind': 'fill',
                },
            )
            conn.commit()

    def _insert_usd_fill_unconverted(self, paper_order_id, fill_id: str):
        import ledger_store as store
        from ledger_store import insert_row

        pf_id = uuid.uuid4()
        with store.connect() as conn:
            insert_row(
                conn,
                'paper_fills',
                {
                    'id': pf_id,
                    'paper_order_id': paper_order_id,
                    'broker_fill_id': fill_id,
                    'qty': 1,
                    'price_cents': 0,
                    'quote_currency': 'USD',
                    'price_quote': Decimal('100'),
                },
            )
            conn.commit()

    def test_gate_b_blocks_when_usd_fill_unconverted(self):
        import gate_b_risk as gb
        from original import load_original

        po = self._seed_order('AAPL', 'nf-' + 'd' * 24)
        self._insert_usd_fill_unconverted(po, 'fill-usd-001')
        risk_now = load_original().risk.parse_now('2026-10-28 10:15')
        d = gb.evaluate_signed_signal(
            {
                'provider': 'tradingview',
                'signal_id': 'OTHER_SIG',
                'symbol': 'MSFT',
                'side': 'buy',
                'asset_class': 'us_equity',
                'entry': '100',
                'stop': '99',
                'target': '102',
                'quantity': 1,
                'strategy_key': 'signal_copy',
            },
            fx=Decimal('5'),
            now=risk_now,
            strategy_phase='paper_limited',
        )
        self.assertEqual(d['decision'], 'rejected')
        self.assertEqual(d['reject_code'], 'UNCONVERTED_FILL')

    def test_loss_anchor_reads_brl_fill(self):
        po = self._seed_order('ITUB4', 'nf-' + 'e' * 24)
        self._insert_brl_fill(po, 'fill-brl-001', -15000)
        snap = la.loss_anchor_snapshot()
        self.assertTrue(snap['daily_pnl_verified'])
        self.assertEqual(snap['daily_pnl_brl'], '-150')
        self.assertFalse(snap['blocks_new_order'])

    def test_reconcile_usd_does_not_invent_brl_anchor(self):
        import ledger_reconcile as lr

        po = self._seed_order('AAPL', 'nf-' + 'f' * 24)
        report = {
            'mode': 'READ_ONLY',
            'activities': {
                'activities': [
                    {
                        'id': 'alpaca-usd-fill-1',
                        'symbol': 'AAPL',
                        'side': 'buy',
                        'qty': '1',
                        'price': '100.00',
                        'quote_currency': 'USD',
                    },
                ],
            },
        }
        out = lr.apply_from_report(report)
        self.assertEqual(out['linked'], 1)
        snap = la.loss_anchor_snapshot()
        self.assertTrue(snap['blocks_new_order'])
        self.assertEqual(snap['reject_code'], 'UNCONVERTED_FILL')
        self.assertEqual(snap['daily_pnl_brl'], '0')


if __name__ == '__main__':
    unittest.main()
