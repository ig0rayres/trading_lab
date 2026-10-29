import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.v4_decision_risk import assess, main

D = {'id':'a', 'kind':'EXTERNAL_SIGNAL','market':'US_EQUITY','symbol':'AAPL', 'decision':'RESEARCH_ONLY', 'paper_approved':False, 'tradable_signal':False, 'orders_sent':0}
R = {'automatic_order_submission':False,'paper_approved':False,'orders_sent':0,'decisions':[D]}

class RiskPreviewTests(unittest.TestCase):
    def test_no_ticket_fails_closed(self):
        x=assess(R)
        self.assertFalse(x['paper_approved'])
        self.assertEqual(x['orders_sent'], 0)
        self.assertIn('NO_EXECUTION_TICKET', x['results'][0]['reasons'])
    def test_arbitrary_ticket_cannot_upgrade(self):
        t={'market':'US_EQUITY','symbol':'AAPL','quantity':1,'side':'buy','entry_brl':100,'stop_brl':99,'verified':True,'trading_mode':'PAPER'}
        snap={'complete':True,'daily_pnl_verified':True,'weekly_pnl_verified':True,'broker_reconciled':True,'positions':[],'daily_pnl_brl':0,'weekly_pnl_brl':0,'available_cash_brl':10000,'has_pending_orders':False}
        x=assess(R,snap,{'a':t})
        self.assertIn('UNVERIFIED_SIGNAL',x['results'][0]['reasons'])
        self.assertIn('NOT_PAPER',x['results'][0]['reasons'])
        self.assertEqual(x['orders_sent'],0)
    def test_mismatched_ticket(self):
        x=assess(R, {}, {'a': {'market':'CRYPTO','symbol':'BTCBRL'}})
        self.assertIn('TICKET_DECISION_MISMATCH',x['results'][0]['reasons'])
    def test_reject_unsafe_decision(self):
        with self.assertRaises(ValueError): assess(dict(R, paper_approved=True))
        with self.assertRaises(ValueError): assess(dict(R, decisions=[dict(D, paper_approved=True)]))
    def test_reject_duplicates(self):
        with self.assertRaises(ValueError): assess(dict(R, decisions=[D,D]))
    def test_cli_no_order(self):
        with tempfile.TemporaryDirectory() as td:
            source=Path(td)/'d.json'; output=Path(td)/'out.json'
            source.write_text(json.dumps(R))
            with patch.dict(os.environ, {'LIVE_TRADING_ENABLED':'false'}):
                self.assertEqual(main(['--decisions',str(source),'--output',str(output)]),0)
            self.assertEqual(json.loads(output.read_text())['orders_sent'],0)
    def test_cli_blocks_live(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'out.json'
            with patch.dict(os.environ, {'LIVE_TRADING_ENABLED':'true'}):
                self.assertEqual(main(['--decisions','missing','--output',str(out)]),2)
            self.assertFalse(out.exists())
