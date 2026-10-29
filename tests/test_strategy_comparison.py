import unittest
from datetime import datetime,timezone
from strategy_comparison import run, VARIANTS
from day_replay import replay_day

class ComparisonTests(unittest.TestCase):
    def bars(self):
        a=[]
        for i in range(78):
            m=570+i*5
            t=f'{m//60:02d}:{m%60:02d}'
            close=102 if i==3 else 100
            a.append(dict(day='2026-10-20',time=t,open=100 if i!=4 else 102,high=max(100,close)+1,low=99,close=close,volume=1000))
        return a
    def test_delayed_filter_gates_initial_signal(self):
        self.assertEqual(replay_day(self.bars(),'LONG')['status'],'EVALUATED')
        self.assertEqual(replay_day(self.bars(),'LONG',earliest='10:00')['status'],'NO_SIGNAL')
    def test_research_only_and_low_sample_no_selection(self):
        days=[]
        for d in [20,21,22,23]:
            days += [dict(b,day=f'2026-10-{d}') for b in self.bars()]
        x=run(['TEST'],sessions=4,fetch=lambda symbol,now:days,now_utc=datetime(2026,10,27,tzinfo=timezone.utc),output=None)
        self.assertEqual(x['orders_sent'],0)
        self.assertFalse(x['authorized_to_trade'])
        self.assertIsNone(x['directions']['LONG']['train_selected_variant'])
        self.assertEqual(len(x['train_sessions'])+len(x['validation_sessions']),4)
        self.assertEqual(set(x['directions']['SHORT']['variants']),set(VARIANTS))
