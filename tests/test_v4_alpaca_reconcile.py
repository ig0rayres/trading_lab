import unittest
from src.v4_alpaca_reconcile import reconcile

class TestReconcile(unittest.TestCase):
    def setUp(self):
        self.activity = {'source': 'ALPACA_PAPER_ACTIVITIES_GET', 'activities': [
            {'id': 'a', 'symbol': 'AAPL', 'side': 'buy', 'qty': '2'}],
            'complete': False, 'history_boundary_verified': False, 'fees_verified': False}
        self.snapshot = {'source': 'ALPACA_PAPER_GET_ONLY', 'broker_reconciled': False}

    def test_missing_raw_positions_cannot_claim_match(self):
        result = reconcile({}, fetch_activities=lambda _: self.activity,
                           fetch_snapshot=lambda _: self.snapshot)
        self.assertIsNone(result['quantity_check'])
        self.assertFalse(result['execution_authorized'])
        self.assertIn('RAW_POSITIONS_NOT_SUPPLIED', result['blocking_reasons'])

    def test_matching_quantities_still_blocked(self):
        positions = [{'symbol': 'AAPL', 'side': 'long', 'qty': '2'}]
        result = reconcile({}, fetch_activities=lambda _: self.activity,
                           fetch_snapshot=lambda _: self.snapshot, raw_positions=positions)
        self.assertTrue(result['quantity_check']['position_quantities_match'])
        self.assertFalse(result['broker_reconciled'])
        self.assertEqual(result['orders_sent'], 0)

    def test_mismatch_reported_not_approved(self):
        result = reconcile({}, fetch_activities=lambda _: self.activity,
                           fetch_snapshot=lambda _: self.snapshot,
                           raw_positions=[{'symbol': 'AAPL', 'side': 'long', 'qty': '1'}])
        self.assertFalse(result['quantity_check']['position_quantities_match'])
        self.assertIn('ACTIVITY_POSITION_MISMATCH', result['blocking_reasons'])

    def test_live_flag_refused(self):
        with self.assertRaisesRegex(ValueError, 'LIVE_TRADING_FORBIDDEN'):
            reconcile({'LIVE_TRADING_ENABLED': 'true'}, fetch_activities=lambda _: None,
                      fetch_snapshot=lambda _: None)

if __name__ == '__main__':
    unittest.main()

class TestPositionFetch(unittest.TestCase):
    def test_positions_fetched_in_readonly_path(self):
        from src.v4_alpaca_reconcile import reconcile
        activities = {'source': 'ALPACA_PAPER_ACTIVITIES_GET', 'activities': [],
                      'complete': False, 'history_boundary_verified': False,
                      'fees_verified': False}
        calls = []
        def positions(_):
            calls.append('positions_get')
            return []
        r = reconcile({}, fetch_activities=lambda _: activities,
                      fetch_snapshot=lambda _: {'broker_reconciled': False},
                      fetch_positions=positions)
        self.assertEqual(calls, ['positions_get'])
        self.assertTrue(r['quantity_check']['position_quantities_match'])
        self.assertFalse(r['execution_authorized'])
