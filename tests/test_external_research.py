import sys
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from external_research import pair_day,net_roundtrip,vwap_fade,summarize


def bars(n=78):
    start=datetime(2026,9,1,9,30,tzinfo=timezone.utc)
    return [{'start':start+timedelta(minutes=5*i),'end':start+timedelta(minutes=5*(i+1)),
             'open':100.,'close':100.,'high':101.,'low':99.,'volume':100} for i in range(n)]

class ExternalResearchTests(unittest.TestCase):
    def test_pair_requires_prior_sessions(self):
        self.assertIsNone(pair_day([100]*19,[100]*19,bars(),bars()))
    def test_pair_has_no_signal_for_constant_ratio(self):
        self.assertIsNone(pair_day([100]*20,[100]*20,bars(),bars()))
    def test_pair_uses_prior_close_only(self):
        a=[100.]*19+[200.];b=[100.]*20
        todaya=bars();todayb=bars()
        self.assertIsNotNone(pair_day(a,b,todaya,todayb,z_enter=1))
        todaya[-1]['close']=1000000
        self.assertEqual(pair_day(a,b,todaya,todayb,z_enter=1)['z_prior_close'],pair_day(a,b,bars(),todayb,z_enter=1)['z_prior_close'])
    def test_fee_reduces_net(self):
        self.assertAlmostEqual(net_roundtrip(100,100,1,10),-.002)
    def test_no_fake_vwap_trigger(self):
        self.assertIsNone(vwap_fade(bars()))
    def test_empty_is_not_profit(self):
        self.assertIsNone(summarize([])['profit_factor'])
