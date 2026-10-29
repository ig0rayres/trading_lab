import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from paper_audit import audit, validate_env, get_json

BASE = dict(ALPACA_BASE_URL='https://paper-api.alpaca.markets', ALPACA_PAPER_TRADE='true',
            LIVE_TRADING_ENABLED='false', ALPACA_API_KEY='example',
            ALPACA_SECRET_KEY='example', USD_BRL_REFERENCE='5.00')

class PaperTests(unittest.TestCase):
    def test_environment(self):
        self.assertEqual(validate_env(BASE), Decimal('5.00'))
    def test_live_rejected(self):
        with self.assertRaises(ValueError): validate_env({**BASE, 'LIVE_TRADING_ENABLED':'true'})
    def test_live_endpoint_rejected(self):
        with self.assertRaises(ValueError): validate_env({**BASE, 'ALPACA_BASE_URL':'https://api.alpaca.markets'})
    def test_missing_fx_rejected(self):
        with self.assertRaises(ValueError): validate_env({**BASE, 'USD_BRL_REFERENCE':''})
    def test_disallowed_request_rejected(self):
        with self.assertRaises(ValueError): get_json('/v2/orders', BASE)
    def test_readonly_does_not_authorize(self):
        r=audit({'status':'ACTIVE','currency':'USD','equity':'5000','cash':'5000'}, [], [], Decimal('5'))
        self.assertFalse(r['paper_execution_authorized'])
        self.assertEqual(r['capital_ceiling_usd'],'1000.00')
        self.assertEqual(r['planned_risk_per_trade_usd'],'10.00')
    def test_overexposure_blocked(self):
        r=audit({'status':'ACTIVE','currency':'USD','equity':'5000','cash':'0'},
                [{'side':'long','symbol':'AAPL','market_value':'1500'}], [],Decimal('5'))
        self.assertIn('CAPITAL_LIMIT_EXCEEDED',r['flags'])
    def test_short_and_orders_detected(self):
        r=audit({'status':'ACTIVE','currency':'USD','equity':'5000','cash':'5000'},
                [{'side':'short','symbol':'TSLA','market_value':'-20'}],[{'id':'x'}],Decimal('5'))
        self.assertIn('SHORT_POSITION_FOUND',r['flags'])
        self.assertIn('OPEN_ORDERS_REQUIRE_REVIEW',r['flags'])

if __name__=='__main__':unittest.main()
