import unittest
from v4_portfolio_merge import merge
from portfolio_risk_v4 import evaluate


class PortfolioMergeTests(unittest.TestCase):
    def setUp(self):
        self.alpaca = {'source': 'ALPACA_PAPER_GET_ONLY', 'complete': False, 'positions': [
            {'market': 'US_EQUITY', 'symbol': 'aapl', 'notional_brl': '1200', 'planned_risk_brl': None}]}
        self.b3 = {'mode': 'SHADOW', 'positions': [
            {'market': 'B3_EQUITY', 'symbol': 'ITUB4', 'notional_brl': '500', 'planned_risk_brl': '20'}]}
        self.crypto = {'mode': 'SHADOW', 'positions': [
            {'market': 'CRYPTO', 'symbol': 'BTCBRL', 'notional_brl': '200', 'planned_risk_brl': '10'}]}

    def test_merges_without_authorizing(self):
        m = merge(self.alpaca, self.b3, self.crypto)
        self.assertEqual(len(m['positions']), 3)
        self.assertFalse(m['complete'])
        self.assertFalse(m['execution_authorized'])
        self.assertIn('STOP_RISK_UNKNOWN:ALPACA:AAPL', m['issues'])
        ticket = {'market': 'B3_EQUITY', 'symbol': 'BBAS3', 'side': 'buy', 'verified': True,
                  'trading_mode': 'PAPER', 'quantity': 1, 'entry_brl': '20', 'stop_brl': '19'}
        self.assertFalse(evaluate(ticket, m)['allowed'])

    def test_rejects_duplicate_crypto_across_sources(self):
        self.alpaca['positions'].append({'market': 'CRYPTO', 'symbol': 'btcbrl', 'notional_brl': '100', 'planned_risk_brl': None})
        with self.assertRaisesRegex(ValueError, 'DUPLICATE'):
            merge(self.alpaca, self.b3, self.crypto)

    def test_rejects_untrusted_market_sources(self):
        self.b3['mode'] = 'LIVE'
        with self.assertRaises(ValueError):
            merge(self.alpaca, self.b3, self.crypto)

    def test_rejects_bad_money_and_unknown_risk(self):
        self.crypto['positions'][0]['notional_brl'] = 'NaN'
        with self.assertRaises(ValueError):
            merge(self.alpaca, self.b3, self.crypto)

    def test_no_fake_broker_attestation(self):
        self.alpaca['broker_reconciled'] = True
        self.b3['complete'] = True
        m = merge(self.alpaca, self.b3, self.crypto)
        self.assertFalse(m['broker_reconciled'])
        self.assertIsNone(m['daily_pnl_brl'])
        self.assertEqual(m['orders_sent'], 0)

if __name__ == '__main__':
    unittest.main()
