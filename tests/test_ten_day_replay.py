import unittest
from datetime import date, timedelta
from ten_day_replay import replay

class ReplayTests(unittest.TestCase):
    def fixture(self):
        start=date(2026,1,1)
        out=[]
        for i in range(85):
            c=100+i*.5
            out.append({'day':(start+timedelta(days=i)).isoformat(),'close':c,'high':c+1,'low':c-1,'volume':1000+i})
        return {'AAA':out,'BBB':[dict(x,close=x['close']*2,high=x['high']*2,low=x['low']*2) for x in out]}
    def test_no_orders_no_trades(self):
        d=replay(self.fixture(),10)
        self.assertEqual(d['orders_sent'],0)
        self.assertEqual(d['simulated_trades'],0)
        self.assertEqual(len(d['decisions']),10)
        self.assertTrue(all(r['decision']=='NO_TRADE' for x in d['decisions'] for r in x['ranked_candidates']))
    def test_causal_prices_future_only_diagnostic(self):
        d=replay(self.fixture(),10)
        first=d['decisions'][0]['ranked_candidates'][0]
        self.assertIsNotNone(first['forward_returns_pct_descriptive_only']['1'])
        self.assertIsNone(d['decisions'][-1]['ranked_candidates'][0]['forward_returns_pct_descriptive_only']['10'])
    def test_short_history_rejected(self):
        with self.assertRaises(ValueError):replay({'AAA':self.fixture()['AAA'][:30]},10)
    def test_invalid_days_rejected(self):
        with self.assertRaises(ValueError):replay(self.fixture(),0)
