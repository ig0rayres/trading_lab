import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from paper_gateway import ticket_gate,process,fingerprint,account_gate
from decimal import Decimal

NOW=datetime(2026,10,28,17,0,tzinfo=timezone.utc)
T={'symbol':'AAPL','side':'buy','asset_class':'us_equity', 'event_id':'sec-123',
   'primary_source_url':'https://www.sec.gov/a',
   'event_verified_at_utc':'2026-10-28T16:00:00+00:00',
   'price_observed_at_utc':'2026-10-28T16:59:45+00:00',
   'entry':'100','stop':'98','target':'104','quantity':2,
   'event_verified':True,'reaction_confirmed':True,'news_first':True}
ENV={'ALPACA_PAPER_TRADE':'true','ALPACA_BASE_URL':'https://paper-api.alpaca.markets',
     'LIVE_TRADING_ENABLED':'false','ALPACA_API_KEY':'mock','ALPACA_SECRET_KEY':'mock',
     'USD_BRL_REFERENCE':'5.0','PAPER_EXECUTION_ENABLED':'false'}
class PaperGatewayTests(unittest.TestCase):
    def test_valid_preview_without_post(self):
        r=process(T,ENV,now=NOW)
        self.assertEqual(r['status'],'PREVIEW_ONLY')
        self.assertEqual(r['orders_sent'],0)
    def test_unverified_blocks(self):
        t={**T,'event_verified':False}
        self.assertIn('NEWS_OR_REACTION_NOT_VERIFIED',ticket_gate(t,Decimal(5),NOW))
    def test_wrong_asset_and_short(self):
        t={**T,'side':'sell','asset_class':'crypto'}
        self.assertIn('ONLY_LONG_US_EQUITY_PAPER_SUPPORTED',ticket_gate(t,Decimal(5),NOW))
    def test_stale_prices(self):
        t={**T,'price_observed_at_utc':'2026-10-28T15:00:00+00:00'}
        self.assertIn('STALE_PRICE',ticket_gate(t,Decimal(5),NOW))
    def test_risk_blocks(self):
        t={**T,'quantity':30}
        self.assertIn('CAPITAL_OR_ONE_PERCENT_RISK_EXCEEDED',ticket_gate(t,Decimal(5),NOW))
    def test_stop_and_reward_blocks(self):
        t={**T,'target':'102'}
        self.assertIn('INVALID_BRACKET_OR_REWARD',ticket_gate(t,Decimal(5),NOW))
    def test_open_orders_block(self):
        a={'status':'ACTIVE','currency':'USD','cash':'5000','equity':'5000'}
        self.assertIn('EXISTING_OPEN_ORDERS',account_gate(a,[],[{'id':'x'}],T,Decimal(5)))
    def test_explicit_confirmation_required(self):
        e={**ENV,'PAPER_EXECUTION_ENABLED':'true'}
        r=process(T,e,now=NOW)
        self.assertEqual(r['status'],'AWAITING_ORDER_SPECIFIC_APPROVAL')
    def test_no_live(self):
        e={**ENV,'LIVE_TRADING_ENABLED':'true'}
        with self.assertRaises(ValueError): process(T,e,now=NOW)
    def test_schema_rejects_unexpected(self):
        self.assertIn('INVALID_TICKET_SCHEMA',ticket_gate({**T,'foo':'bar'},Decimal(5),NOW))

if __name__=='__main__':unittest.main()
