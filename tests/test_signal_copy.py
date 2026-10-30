import sys, unittest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signal_copy import preflight, sign

class SignalCopyTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,28,17,0,tzinfo=timezone.utc)
        self.secret='a'*32
        self.s={'provider':'sample','signal_id':'ABC-0001','symbol':'AAPL','side':'buy','asset_class':'us_equity',
                'sent_at_utc':self.now.isoformat(),'entry':'100','stop':'99','target':'102','quantity':1,'ttl_seconds':30}
        self.s['provider_signature']=sign(self.s,self.secret)
    def check(self): return preflight(self.s,self.secret,Decimal('5'),self.now)
    def test_valid_preview_no_order(self):
        x=self.check(); self.assertEqual(x['status'],'SIGNAL_ACCEPTED_RISK_PREVIEW');self.assertEqual(x['orders_sent'],0)
    def test_bad_signature(self):
        self.s['quantity']=2;self.assertIn('AUTH_FAILED',self.check()['reasons'])
    def test_stale(self):
        self.s['sent_at_utc']=(self.now-timedelta(minutes=2)).isoformat();self.s['provider_signature']=sign(self.s,self.secret)
        self.assertIn('EXPIRED_OR_FUTURE_SIGNAL',self.check()['reasons'])
    def test_risk(self):
        self.s['quantity']=11;self.s['provider_signature']=sign(self.s,self.secret)
        self.assertIn('RISK_OR_NOTIONAL_LIMIT',self.check()['reasons'])
    def test_short_blocked(self):
        self.s['side']='sell';self.s['provider_signature']=sign(self.s,self.secret)
        self.assertIn('LONG_US_EQUITY_ONLY',self.check()['reasons'])
    def test_unrecognized_field(self):
        self.s['news_first']=True
        self.assertIn('INVALID_SCHEMA',self.check()['reasons'])
    def test_strategy_key_allowed_when_signed(self):
        self.s['strategy_key']='signal_copy'
        self.s['provider_signature']=sign(self.s,self.secret)
        self.assertEqual(self.check()['status'],'SIGNAL_ACCEPTED_RISK_PREVIEW')
