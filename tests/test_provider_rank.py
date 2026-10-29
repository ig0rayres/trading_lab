import sys, unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from provider_rank import analyze
NOW=datetime(2026,10,28,tzinfo=timezone.utc)
def provider(name, n=35, gain=0.3, verified=True):
    return {'id':name,'verified':verified,'asset_classes':['us_equity'],
            'track_record_start':(NOW-timedelta(days=200)).isoformat(),
            'trades':[{'closed_at':(NOW-timedelta(days=170)+timedelta(days=i*4)).isoformat(),
                       'net_pnl_pct':gain,'risk_pct':1} for i in range(n)]}
class ProviderRankTests(unittest.TestCase):
    def test_select_top_three(self):
        result=analyze({'providers':[provider('a',gain=0.5),provider('b',gain=0.4),provider('c',gain=0.3),provider('d',gain=0.2)]},NOW)
        self.assertEqual(result['paper_priority_top_3'],['a','b','c'])
        self.assertEqual(result['orders_sent'],0)
    def test_unverified_rejected(self):
        r=analyze({'providers':[provider('a',verified=False)]},NOW)
        self.assertEqual(r['paper_priority_top_3'],[])
    def test_low_sample_rejected(self):
        r=analyze({'providers':[provider('a',n=8)]},NOW)
        self.assertIn('LOW_SAMPLE',r['top_10'][0]['reasons'])
    def test_negative_rejected(self):
        r=analyze({'providers':[provider('a',gain=-0.1)]},NOW)
        self.assertEqual(r['paper_priority_top_3'],[])
    def test_future_trade_rejected(self):
        p=provider('a');p['trades'][0]['closed_at']=(NOW+timedelta(days=1)).isoformat()
        r=analyze({'providers':[p]},NOW)
        self.assertIn('INVALID_TRADE_DATA',r['top_10'][0]['reasons'])
    def test_duplicate_provider_rejected(self):
        p=provider('a')
        with self.assertRaises(ValueError): analyze({'providers':[p,p]},NOW)
if __name__=='__main__':unittest.main()
