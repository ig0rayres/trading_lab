import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from lab import signal,simulate,report
class LabTests(unittest.TestCase):
 def bars(self,n=14):
  return [{'timestamp':f'2026-10-19T09:{30+i*2:02d}:00-04:00','session':'2026-10-19','open':100.,'high':101.,'low':99.,'close':100.,'volume':100.} for i in range(n)]
 def test_no_future_leak(self):
  b=self.bars();b[5]['close']=102;b[5]['high']=103
  self.assertFalse(signal('orb',b,4));self.assertTrue(signal('orb',b,5))
 def test_next_bar_entry(self):
  b=self.bars();b[5]['close']=102;b[5]['high']=103;b[6]['open']=104;b[6]['high']=105;b[6]['low']=103;b[6]['close']=104
  t=simulate(b,'orb',0,0);self.assertEqual(len(t),1);self.assertEqual(t[0]['entry'],104)
 def test_no_trade_missing_data(self):self.assertEqual(report([])['status'],'INSUFFICIENT_DATA')
 def test_stop_priority(self):
  b=self.bars();b[5]['close']=102;b[5]['high']=103;b[6].update(open=102,high=110,low=90,close=102)
  t=simulate(b,'orb',0,0);self.assertAlmostEqual(t[0]['exit'],102*(1-.0075))
if __name__=='__main__':unittest.main()
