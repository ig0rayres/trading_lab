import unittest
from v4_order_lifecycle import reconcile_snapshot


def order(**kw):
    x = {'id': 'a', 'status': 'filled', 'symbol': 'AAPL', 'side': 'buy', 'qty': '2',
         'filled_qty': '2', 'filled_avg_price': '100', 'order_class': 'bracket', 'legs': [
         {'id': 'tp', 'status': 'new', 'symbol': 'AAPL', 'side': 'sell', 'qty': '2', 'filled_qty': '0'},
         {'id': 'sl', 'status': 'held', 'symbol': 'AAPL', 'side': 'sell', 'qty': '2', 'filled_qty': '0'}]}
    x.update(kw)
    return x


class LifecycleTests(unittest.TestCase):
    def test_filled_entry_not_closed_trade(self):
        r = reconcile_snapshot({'orders': [order()]})
        self.assertEqual(len(r['orders']), 3)
        self.assertFalse(r['positions_closed_verified'])
        self.assertIsNone(r['realized_pnl_brl'])
        self.assertFalse(r['execution_authorized'])
    def test_partial_entry(self):
        r = reconcile_snapshot({'orders': [order(status='partially_filled', filled_qty='1', filled_avg_price='99')]})
        self.assertTrue(r['has_partial_fills'])
    def test_bracket_without_legs_is_not_safe(self):
        r = reconcile_snapshot({'orders': [order(legs=None)]})
        self.assertIn('MISSING_BRACKET_LEGS:a', r['issues'])
    def test_no_double_count_duplicate_order_id(self):
        with self.assertRaisesRegex(ValueError, 'DUPLICATE'):
            reconcile_snapshot({'orders': [order(), order()]})
    def test_invalid_filled_status(self):
        with self.assertRaisesRegex(ValueError, 'INCONSISTENT'):
            reconcile_snapshot({'orders': [order(filled_qty='1')]})
    def test_invalid_partial_status(self):
        with self.assertRaisesRegex(ValueError, 'INCONSISTENT'):
            reconcile_snapshot({'orders': [order(status='partially_filled', filled_qty='0', filled_avg_price=None)]})
    def test_nan_is_blocked(self):
        with self.assertRaises(ValueError):
            reconcile_snapshot({'orders': [order(qty='NaN')]})
    def test_cross_symbol_leg_blocked(self):
        o = order()
        o['legs'][0]['symbol'] = 'MSFT'
        with self.assertRaisesRegex(ValueError, 'MISMATCHED'):
            reconcile_snapshot({'orders': [o]})
    def test_no_data_does_not_attest_completion(self):
        r = reconcile_snapshot({'orders': []})
        self.assertFalse(r['broker_reconciled'])
    def test_unknown_status_blocked(self):
        with self.assertRaises(ValueError):
            reconcile_snapshot({'orders': [order(status='unknown')]})

if __name__ == '__main__': unittest.main()
