import unittest
from src.v4_fill_position_check import compare


def payload():
    return {'source': 'ALPACA_PAPER_ACTIVITIES_GET', 'complete': False,
            'activities': [{'id': '1', 'symbol': 'AAPL', 'side': 'buy', 'qty': '2'},
                           {'id': '2', 'symbol': 'AAPL', 'side': 'sell', 'qty': '0.5'}]}


class FillPositionCheckTests(unittest.TestCase):
    def test_matching_still_not_reconciled(self):
        result = compare(payload(), [{'symbol': 'AAPL', 'side': 'long', 'qty': '1.5'}])
        self.assertTrue(result['position_quantities_match'])
        self.assertFalse(result['broker_reconciled'])
        self.assertFalse(result['execution_authorized'])
        self.assertIn('INCOMPLETE_ACTIVITY_HISTORY', result['blocking_reasons'])

    def test_missing_historical_buy_does_not_pass(self):
        p = payload()
        p['activities'] = [p['activities'][1]]
        r = compare(p, [])
        self.assertFalse(r['position_quantities_match'])

    def test_mismatched_qty(self):
        r = compare(payload(), [{'symbol': 'AAPL', 'side': 'long', 'qty': '1'}])
        self.assertEqual(len(r['differences']), 1)

    def test_duplicate_fill_rejected(self):
        p = payload()
        p['activities'].append(p['activities'][0])
        with self.assertRaises(ValueError):
            compare(p, [])

    def test_invalid_numeric_rejected(self):
        p = payload()
        p['activities'][0]['qty'] = 'NaN'
        with self.assertRaises(ValueError):
            compare(p, [])

    def test_short_position_rejected(self):
        with self.assertRaises(ValueError):
            compare(payload(), [{'symbol': 'AAPL', 'side': 'short', 'qty': '1.5'}])

    def test_untrusted_activity_source_rejected(self):
        p = payload()
        p['source'] = 'USER_GUESSED'
        with self.assertRaises(ValueError):
            compare(p, [])


if __name__ == '__main__':
    unittest.main()
