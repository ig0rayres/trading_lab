import datetime as dt
import json
import sys
import tempfile
import unittest
from types import SimpleNamespace
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import history
import original
NY=ZoneInfo('America/New_York')

class EntryFake:
    @staticmethod
    def session(d):
        return ((dt.time(9,30),dt.time(16,0)) if d.weekday()<5 else None)
    @staticmethod
    def evaluate(chart,now_utc,**kwargs):
        # Fake returns first closed signal from a known day, not computed from future.
        start=dt.datetime.fromtimestamp(chart['bars'][0]['t'],NY)
        return {'status':'triggered','trigger':{'close_time':'09:50'},
                'opening_range':{'high':101.,'low':99.,'complete':True,'bars':3}}

class ExitFake:
    @staticmethod
    def parse_stop(x):return 'or_mid',None
    @staticmethod
    def parse_target(x):return 'r',Decimal(x[:-1])
    @staticmethod
    def compute(entry,sr,sp,tr,tp,or_high,or_low):
        e=Decimal(str(entry)).quantize(Decimal('.01'))
        stop=Decimal('100.00')
        return {'entry':e,'stop':stop,'target':(e+tp*(e-stop)).quantize(Decimal('.01'))}

class BudgetFake:
    @staticmethod
    def size_trade(plan,cfg,**kw):return {'qty':10,'refusal':None}
    @staticmethod
    def bracket_order(x):return {'symbol':'TEST','qty':'10'}

class RiskFake:
    @staticmethod
    def check(orders,cfg,**kw):return {'results':[{'verdict':'PASS','reasons':[]}]}

class HistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig=SimpleNamespace(entry=EntryFake(),exit=ExitFake(),budget=BudgetFake(),risk=RiskFake(),
                                 commit='fake-sha')
        cls.date=dt.date(2026,10,19)
    def chart(self,high_bars=None,missing=None,duplicate=False):
        b=[]
        for i in range(78):
            if i==missing:continue
            time=dt.datetime.combine(self.date,dt.time(9,30),NY)+dt.timedelta(minutes=5*i)
            hi=107.0 if high_bars and i in high_bars else (101.0 if i<3 else 103.0)
            lo=99 if i<3 else 102
            op=100 if i<3 else 102.5
            close=100 if i<3 else 102.7
            if i==3: hi,lo,op,close=102.5,100.,101.5,102.
            b.append({'t':int(time.timestamp()),'o':op,'h':hi,'l':lo,'c':close,'v':100})
        if duplicate:b.append(dict(b[-1]))
        return {'symbol':'TEST','bars':b}
    def test_completed_session(self):
        b,err=history.session_bars(self.orig,self.chart(),self.date)
        self.assertEqual(err,None);self.assertEqual(len(b),78)
    def test_reject_missing_grid(self):
        _,err=history.session_bars(self.orig,self.chart(missing=7),self.date)
        self.assertIn('INCOMPLETE_SESSION',err)
    def test_reject_duplicate_bars(self):
        _,err=history.session_bars(self.orig,self.chart(duplicate=True),self.date)
        self.assertEqual(err,'DUPLICATE_BAR')
    def test_two_original_module_calls(self):
        ch=self.chart(high_bars=[7]);bars,_=history.session_bars(self.orig,ch,self.date)
        row=history.simulate_day(self.orig,ch,bars,self.date,1)
        self.assertEqual(row['risk_verdict'],'PASS')
        self.assertEqual(row['exit_reason'],'target')
    def test_stop_first_on_ambiguous_bar(self):
        ch=self.chart(high_bars=[7]);ch['bars'][7]['l']=99
        bars,_=history.session_bars(self.orig,ch,self.date)
        row=history.simulate_day(self.orig,ch,bars,self.date,1)
        self.assertEqual(row['exit_reason'],'stop')
        self.assertLess(row['net_r'],0)
    def test_flat_by_1555_without_lookahead(self):
        ch=self.chart();bars,_=history.session_bars(self.orig,ch,self.date)
        row=history.simulate_day(self.orig,ch,bars,self.date,2)
        self.assertEqual(row['exit_reason'],'flat')
        self.assertEqual(dt.datetime.fromisoformat(row['exit_at']).time(),dt.time(15,55))
    def test_no_same_day_screening_dependency(self):
        import inspect
        self.assertNotIn('watchlist',inspect.getsource(history.simulate_day).lower())
    def test_parser_rejects_no_symbols(self):
        import argparse
        with self.assertRaisesRegex(ValueError,'Provide'):
            history.parse_symbol_list(SimpleNamespace(symbols='',symbols_file='',max_symbols=30))
    def test_original_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(RuntimeError,'Original module missing'):
                original.load_original(td)
    def test_metrics(self):
        r=[{'net_r':1.,'risk_verdict':'PASS'},{'net_r':-1.,'risk_verdict':'BLOCK'}]
        m=history.metrics(r)
        self.assertEqual(m['mean_net_r'],0)
        self.assertEqual(m['risk_pass'],1)

if __name__=='__main__':unittest.main()
