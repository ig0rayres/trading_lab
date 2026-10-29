import unittest
from v4_broker_snapshot import build_snapshot, collect
from portfolio_risk_v4 import evaluate


class BrokerSnapshotTests(unittest.TestCase):
    def account(self):
        return {'status': 'ACTIVE', 'currency': 'USD', 'trading_blocked': False, 'cash': '20000'}

    def test_empty_alpaca_never_approves_all_markets(self):
        s = build_snapshot(self.account(), [], [], 5)
        self.assertFalse(s['complete'])
        self.assertFalse(s['broker_reconciled'])
        candidate = {'market': 'B3_EQUITY', 'symbol': 'ITUB4', 'side': 'buy', 'verified': True,
                     'trading_mode': 'PAPER', 'quantity': 5, 'entry_brl': '40', 'stop_brl': '38'}
        self.assertFalse(evaluate(candidate, s)['allowed'])

    def test_positions_retained_with_unknown_stop(self):
        p = [{'symbol': 'AAPL', 'side': 'long', 'market_value': '500', 'asset_class': 'us_equity'}]
        s = build_snapshot(self.account(), p, [], 5)
        self.assertEqual(s['positions'][0]['notional_brl'], '2500')
        self.assertIsNone(s['positions'][0]['planned_risk_brl'])

    def test_crypto_market_class(self):
        p = [{'symbol': 'BTCUSD', 'side': 'long', 'market_value': '250', 'asset_class': 'crypto'}]
        self.assertEqual(build_snapshot(self.account(), p, [], 5)['positions'][0]['market'], 'CRYPTO')

    def test_open_orders_are_blocked(self):
        s = build_snapshot(self.account(), [], [{'id': 'a'}], 5)
        self.assertTrue(s['has_pending_orders'])
        self.assertFalse(s['execution_authorized'])

    def test_rejects_invalid_broker_data(self):
        invalid = ([{'symbol': 'AAPL', 'side': 'short', 'market_value': '-20', 'asset_class': 'us_equity'}],
                   [{'symbol': 'AAPL', 'side': 'long', 'market_value': '10', 'asset_class': 'unknown'}],
                   [{'symbol': 'AAPL', 'side': 'long', 'market_value': '10', 'asset_class': 'us_equity'}] * 2)
        for items in invalid:
            with self.subTest(items=items), self.assertRaises(ValueError):
                build_snapshot(self.account(), items, [], 5)

    def test_get_only_allowlisted_paths(self):
        seen = []
        def getter(path, env):
            seen.append(path)
            return {'/v2/account': self.account(), '/v2/positions': [], '/v2/orders?status=open&limit=500': []}[path]
        env = {'LIVE_TRADING_ENABLED': 'false', 'ALPACA_PAPER_TRADE': 'true',
               'ALPACA_BASE_URL': 'https://paper-api.alpaca.markets',
               'ALPACA_API_KEY': 'fake', 'ALPACA_SECRET_KEY': 'fake', 'USD_BRL_REFERENCE': '5'}
        self.assertEqual(collect(env, getter=getter)['source'], 'ALPACA_PAPER_GET_ONLY')
        self.assertEqual(len(seen), 3)


if __name__ == '__main__':
    unittest.main()
