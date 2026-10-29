import hmac
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from src import signal_paper_runner as x
from src.signal_copy import sign

class PaperRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ledger=str(Path(self.tmp.name)/'journal.jsonl')
        self.env={'LIVE_TRADING_ENABLED':'false','ALPACA_PAPER_TRADE':'true',
                  'ALPACA_BASE_URL':'https://paper-api.alpaca.markets',
                  'ALPACA_API_KEY':'test','ALPACA_SECRET_KEY':'test',
                  'USD_BRL_REFERENCE':'5','SIGNAL_COPY_SECRET':'x'*32}
        self.signal={'provider':'provider_1','signal_id':'signal_12345',
                     'symbol':'AAPL','side':'buy','asset_class':'us_equity',
                     'sent_at_utc':datetime.now(timezone.utc).isoformat(),
                     'entry':100,'stop':99,'target':102,'quantity':1,'ttl_seconds':60}
        self.signal['provider_signature']=sign(self.signal,self.env['SIGNAL_COPY_SECRET'])
    def test_preview_does_not_call_broker(self):
        def fail(*a,**k): raise AssertionError('broker called')
        r=x.run(self.signal,self.env,self.ledger,broker_get=fail,broker_post=fail)
        self.assertEqual(r['status'],'PREVIEW_ONLY')
        self.assertFalse(Path(self.ledger).exists())
    def test_bad_signature_blocked(self):
        self.signal['provider_signature']='bad'
        self.assertEqual(x.run(self.signal,self.env,self.ledger)['status'],'BLOCKED')
    def test_auto_mode_requires_attestation(self):
        self.env.update(PAPER_SIGNAL_AUTO_ENABLED='true',PAPER_EXECUTION_ENABLED='true')
        self.assertEqual(x.run(self.signal,self.env,self.ledger)['status'],'BLOCKED')
    def test_unknown_broker_state_blocks_retry(self):
        self.env.update(PAPER_SIGNAL_AUTO_ENABLED='true',PAPER_EXECUTION_ENABLED='true',
                        PAPER_SIGNAL_ACCOUNT_ACK='I_AUTHORIZE_ALPACA_PAPER_ONLY',PAPER_DAILY_RISK_CONFIRMED='true')
        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status':'ACTIVE','currency':'USD','trading_blocked':False,'cash':'2000','equity':'2000'}
            return []
        snapshot=Path(self.tmp.name)/'risk.json'
        snapshot.write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),
            'alpaca_positions_count':0,'alpaca_open_orders_count':0,'complete':True,
            'daily_pnl_verified':True,'weekly_pnl_verified':True,'broker_reconciled':True,
            'positions':[],'daily_pnl_brl':'0','weekly_pnl_brl':'0',
            'available_cash_brl':'10000','has_pending_orders':False}))
        self.env['V4_RISK_SNAPSHOT_FILE']=str(snapshot)
        def broken(*a): raise TimeoutError()
        first=x.run(self.signal,self.env,self.ledger,broker_get=getter,broker_post=broken)
        self.assertEqual(first['status'],'UNKNOWN_DO_NOT_RETRY')
        second=x.run(self.signal,self.env,self.ledger,broker_get=getter,broker_post=broken)
        self.assertEqual(second['status'],'BLOCKED')
        self.assertEqual(second['reasons'],['ALREADY_ATTEMPTED_RECONCILE_FIRST'])
    def test_auto_mode_blocks_without_consolidated_risk_snapshot(self):
        self.env.update(PAPER_SIGNAL_AUTO_ENABLED='true', PAPER_EXECUTION_ENABLED='true',
                        PAPER_SIGNAL_ACCOUNT_ACK='I_AUTHORIZE_ALPACA_PAPER_ONLY',
                        PAPER_DAILY_RISK_CONFIRMED='true')
        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status':'ACTIVE','currency':'USD','trading_blocked':False,
                        'cash':'2000','equity':'2000'}
            return []
        def forbidden(*args): raise AssertionError('Order should not be posted')
        result=x.run(self.signal,self.env,self.ledger,broker_get=getter,broker_post=forbidden)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertIn('V4_PORTFOLIO_SNAPSHOT_REQUIRED',result['reasons'])
    def test_short_blocked(self):
        self.signal['side']='sell'
        self.signal['provider_signature']=sign(self.signal,self.env['SIGNAL_COPY_SECRET'])
        self.assertEqual(x.run(self.signal,self.env,self.ledger)['status'],'BLOCKED')

if __name__=='__main__':unittest.main()
