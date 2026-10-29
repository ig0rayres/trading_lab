import json
import sys
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from market_opportunities import inspect
from trading_dashboard_data import summary
from prodigy_rank import WINDOW_DAYS
from v4_readiness import readiness

class V4Tests(unittest.TestCase):
    def item(self,market='B3_EQUITY',dropped=True):
        prices=[100,102,100,98,96,90] if dropped else [100,101,102,103,104,105]
        at=datetime(2026,10,29,tzinfo=timezone.utc)
        return {'market':market,'symbol':'ITUB4' if market=='B3_EQUITY' else 'BTC/USD',
                'quality_verified':True,'event_reviewed':True,
                'bars':[{'at':(at+timedelta(minutes=i)).isoformat(),'close':v,'high':v+1,'low':v-1,'volume':1000} for i,v in enumerate(prices)]}
    def test_prodigy_15_days(self):self.assertEqual(WINDOW_DAYS,15)
    def test_drop_trigger_b3(self):
        result=inspect(self.item());self.assertTrue(result['radar_candidate']);self.assertFalse(result['paper_approved']);self.assertEqual(result['orders_sent'],0)
    def test_no_drop(self):self.assertFalse(inspect(self.item(dropped=False))['radar_candidate'])
    def test_crypto_volatility_gate(self):
        result=inspect(self.item(market='CRYPTO'));self.assertTrue(result['radar_candidate']);self.assertEqual(result['mode'],'SHADOW_ONLY')
    def test_unverified_quality_flag(self):
        x=self.item();x['quality_verified']=False;self.assertIn('QUALITY_UNVERIFIED',inspect(x)['issues'])
    def test_unordered_rejected(self):
        x=self.item();x['bars'][-1]['at']=x['bars'][0]['at'];self.assertRaises(ValueError,inspect,x)
    def test_nan_rejected(self):
        x=self.item();x['bars'][-1]['close']=float('nan');self.assertRaises(ValueError,inspect,x)
    def test_unsupported_market(self):
        x=self.item();x['market']='FOREX';self.assertRaises(ValueError,inspect,x)
    def test_readiness_blocks_unsafe_live(self):
        with tempfile.TemporaryDirectory() as p:
            r=readiness({"LIVE_TRADING_ENABLED":"true","PAPER_SIGNAL_AUTO_ENABLED":"true"},Path(p))
            self.assertFalse(r["autonomous_multimarket_ready"])
            self.assertIn("LIVE_FLAG_UNSAFE",r["blockers"])
            self.assertIn("AUTO_SIGNAL_ON_REQUIRES_INDEPENDENT_RISK_VALIDATION",r["blockers"])
    def test_empty_dashboard_no_false_profit(self):
        with tempfile.TemporaryDirectory() as p:
            d=summary(Path(p));self.assertIsNone(d['realized_gross_pnl_usd']);self.assertIsNone(d['win_rate'])
    def test_duplicate_snapshots_only_latest(self):
        with tempfile.TemporaryDirectory() as p:
            x=Path(p)/'paper';x.mkdir(); rows=[{'client_order_id':'demo-1','status':'MONITORED','entry_qty':'1','remaining_qty':'1','realized_gross_pnl_usd':'0'}, {'client_order_id':'demo-1','status':'MONITORED','entry_qty':'1','remaining_qty':'0','realized_gross_pnl_usd':'4'}]
            (x/'order-snapshots.jsonl').write_text('\n'.join(map(json.dumps,rows)))
            d=summary(Path(p));self.assertEqual(d['paper_orders_monitored'],1);self.assertEqual(d['realized_gross_pnl_usd'],'4');self.assertEqual(d['closed_orders_with_pnl'],1)
if __name__=='__main__':unittest.main()
