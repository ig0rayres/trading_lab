import datetime as dt
import sys, unittest
from pathlib import Path
from zoneinfo import ZoneInfo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from orb_batch import eval_hit
NY=ZoneInfo('America/New_York')
class BatchTests(unittest.TestCase):
    def setUp(self):
        self.date='2026-10-26'
        self.hit={'symbol':'TEST','at':'9:50 AM','price':102,'or_high':101,'or_low':99}
        self.bars=[]
        for i in range(78):
            start=dt.datetime(2026,10,26,9,30,tzinfo=NY)+dt.timedelta(minutes=5*i)
            self.bars.append({'start':start,'end':start+dt.timedelta(minutes=5),'open':102,'high':102.5,'low':101.9,'close':102,'volume':100})
    def test_target(self):
        self.bars[5]['high']=107
        t=eval_hit(self.hit,self.bars,self.date,2,0,0)
        self.assertEqual(t['exit_reason'],'target')
        self.assertEqual(t['entry_at'][-6:],'-04:00')
    def test_ambiguous_bar_is_stop(self):
        self.bars[4]['low']=99
        self.bars[4]['high']=108
        t=eval_hit(self.hit,self.bars,self.date,2,0,0)
        self.assertEqual(t['exit_reason'],'stop')
    def test_missing_flat(self):
        with self.assertRaisesRegex(ValueError,'SESSION_NOT_FINISHED'):
            eval_hit(self.hit,self.bars[:10],self.date,2,0,0)
    def test_intraday_marks_unresolved(self):
        trade=eval_hit(self.hit,self.bars[:9],self.date,2,0,0,intraday=True)
        self.assertEqual(trade['exit_reason'],'mark_to_market_partial')
        self.assertEqual(trade['result_type'],'PARTIAL_INTRADAY')
    def test_intraday_triggered_exit(self):
        data=[dict(x) for x in self.bars[:9]]
        data[6]['high']=110
        trade=eval_hit(self.hit,data,self.date,2,0,0,intraday=True)
        self.assertEqual(trade['exit_reason'],'target')
    def test_incomplete_bar_excluded(self):
        from orb_batch import bars_for_date
        from datetime import timedelta
        ts=[int(x['start'].timestamp()) for x in self.bars[:5]]
        ts.append(int(self.bars[5]['start'].timestamp())+32)
        d={'chart':{'result':[{'timestamp':ts,'indicators':{'quote':[{'open':[102]*6,'high':[103]*6,'low':[101]*6,'close':[102]*6,'volume':[10]*6}]}}]}}
        asof=self.bars[4]['end']
        self.assertEqual(len(bars_for_date(d,self.date,as_of=asof)),5)
    def test_entry_next_bar(self):
        t=eval_hit(self.hit,self.bars,self.date,1,0,0)
        self.assertIn('09:50:00',t['entry_at'])
if __name__=='__main__':unittest.main()
