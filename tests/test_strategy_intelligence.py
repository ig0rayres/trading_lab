import sys,unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from strategy_intelligence import evaluate

NOW=datetime(2026,10,28,tzinfo=timezone.utc)
def item(**kw):
    base={'id':'alpha','evidence_verified':True,'execution_reconciled':True,
          'prior_paper_approved':True,'trades':[{'closed_at':(NOW-timedelta(hours=3)).isoformat(),'net_pnl_brl':10}]}
    base.update(kw);return base
class IntelligenceTests(unittest.TestCase):
    def test_approved_with_evidence(self): self.assertEqual(evaluate({'strategies':[item()]},'daily',NOW)['strategies'][0]['status'],'PAPER_ELIGIBLE')
    def test_no_automatic_promotion(self): self.assertEqual(evaluate({'strategies':[item(prior_paper_approved=False)]},'daily',NOW)['strategies'][0]['status'],'OBSERVATION')
    def test_risk_breach_suspend(self): self.assertEqual(evaluate({'strategies':[item(risk_breach=True)]},'daily',NOW)['strategies'][0]['status'],'SUSPENDED')
    def test_unknown_open_order_suspend(self): self.assertEqual(evaluate({'strategies':[item(open_orders_unknown=True)]},'weekly',NOW)['strategies'][0]['status'],'SUSPENDED')
    def test_no_evidence_no_approval(self): self.assertEqual(evaluate({'strategies':[item(evidence_verified=False)]},'monthly',NOW)['strategies'][0]['status'],'OBSERVATION')
    def test_no_trade_no_approval(self): self.assertEqual(evaluate({'strategies':[item(trades=[])]},'daily',NOW)['strategies'][0]['status'],'OBSERVATION')
    def test_future_trade_suspend(self): self.assertEqual(evaluate({'strategies':[item(trades=[{'closed_at':(NOW+timedelta(days=1)).isoformat(),'net_pnl_brl':5}])]},'daily',NOW)['strategies'][0]['status'],'SUSPENDED')
    def test_duplicate_ids(self):
        with self.assertRaises(ValueError): evaluate({'strategies':[item(),item()]},'daily',NOW)
    def test_negative_threshold(self): self.assertEqual(evaluate({'strategies':[item(trades=[{'closed_at':NOW.isoformat(),'net_pnl_brl':-151}])]},'daily',NOW)['strategies'][0]['status'],'SUSPENDED')
    def test_read_only(self): self.assertFalse(evaluate({'strategies':[item()]},'daily',NOW)['execution_authorized'])
