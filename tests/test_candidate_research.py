import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from candidate_research import build,summarize,nav_returns
class Candidates(unittest.TestCase):
 def test_empty(self):
  self.assertEqual(summarize([])['all']['days'],0)
 def test_one_day_lag(self):
  p={'2024-01-01':{'SPY':100},'2024-01-02':{'SPY':110},'2024-01-03':{'SPY':99}}
  rows=nav_returns(p,lambda d,i,ds,prices:{'SPY':1} if i>=1 else {},0)
  self.assertEqual(rows[0]['net_return'],0)
  self.assertAlmostEqual(rows[1]['net_return'],-.1)
 def test_fee_reduces(self):
  p={'2024-01-01':{'SPY':100},'2024-01-02':{'SPY':100}}
  x=nav_returns(p,lambda *a:{'SPY':1},10)
  self.assertAlmostEqual(x[0]['equity'],(1-.001)*(1-.001))
 def test_tom(self):
  import datetime
  days=[(datetime.date(2023,1,1)+datetime.timedelta(days=i)).isoformat() for i in range(500)]
  p={d:{s:100+0.01*i for s in ['SPY','QQQ','IWM','GLD','TLT','AAPL','MSFT','NVDA','AMD','AMZN','META','GOOGL']} for i,d in enumerate(days)}
  r=build(p,'2024-01-01','2024-05-01',10)
  self.assertEqual(len(r),4)
  self.assertGreater(len(r['turn_of_month_spy']),0)
if __name__=='__main__':unittest.main()
