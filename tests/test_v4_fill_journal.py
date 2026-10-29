import copy
import unittest
from v4_fill_journal import update_journal, inspect


def snap(qty='0', status='new', avg=None, oid='one'):
    return {'orders': [{'id': oid, 'symbol': 'AAPL', 'side': 'buy', 'status': status, 'qty': '3', 'filled_qty': qty, 'filled_avg_price': avg}]}


class FillJournalTests(unittest.TestCase):
    def test_new_and_repeat_are_idempotent(self):
        first, meta = update_journal(None, snap())
        second, repeat = update_journal(first, snap())
        self.assertEqual(len(second['events']), 1)
        self.assertEqual(repeat['new_events'], 0)
        self.assertFalse(repeat['broker_reconciled'])
    def test_incremental_partial_then_full(self):
        journal, _ = update_journal(None, snap('1', 'partially_filled', '100'))
        journal, _ = update_journal(journal, snap('2', 'partially_filled', '101'))
        journal, _ = update_journal(journal, snap('3', 'filled', '102'))
        self.assertEqual([x['incremental_filled_qty'] for x in journal['events']], ['1', '1', '1'])
        self.assertEqual(len(inspect(journal)[0]), 1)
    def test_fill_regression_rejected(self):
        journal, _ = update_journal(None, snap('2', 'partially_filled', '100'))
        with self.assertRaisesRegex(ValueError, 'FILL_REGRESSION'):
            update_journal(journal, snap('1', 'partially_filled', '100'))
    def test_changed_price_without_new_qty_rejected(self):
        journal, _ = update_journal(None, snap('1', 'partially_filled', '100'))
        with self.assertRaisesRegex(ValueError, 'FILL_PRICE_CHANGED'):
            update_journal(journal, snap('1', 'partially_filled', '101'))
    def test_tamper_rejected(self):
        journal, _ = update_journal(None, snap('1', 'partially_filled', '100'))
        altered = copy.deepcopy(journal)
        altered['events'][0]['symbol'] = 'MSFT'
        with self.assertRaisesRegex(ValueError, 'TAMPERED'):
            update_journal(altered, snap('2', 'partially_filled', '100'))
    def test_multiple_orders_are_not_closed_trade(self):
        journal, meta = update_journal(None, {'orders': snap('3', 'filled', '100')['orders'] + snap('3', 'filled', '102', 'two')['orders']})
        self.assertEqual(meta['new_events'], 2)
        self.assertIsNone(meta['realized_pnl_brl'])
        self.assertFalse(meta['execution_authorized'])
    def test_reject_invalid_broker_snapshot(self):
        with self.assertRaises(ValueError):
            update_journal(None, snap('4', 'filled', '100'))

if __name__ == '__main__': unittest.main()
