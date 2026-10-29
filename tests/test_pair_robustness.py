import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pair_robustness import analyze

class PairRobustnessTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(analyze([])['baseline']['n'],0)
    def test_extra_costs_always_reduce_mean(self):
        r=analyze([{'symbol':'A:B','date':'2026-10-01','net_pct':'.06'}, {'symbol':'A:B','date':'2026-10-02','net_pct':'-.02'}])
        self.assertAlmostEqual(r['additional_one_way_bps_per_leg']['5']['mean_net_pct'], -.08)
    def test_temporal_by_day(self):
        r=analyze([{'symbol':'A:B','date':'2026-10-01','net_pct':'1'}, {'symbol':'C:D','date':'2026-10-01','net_pct':'1'}, {'symbol':'A:B','date':'2026-10-02','net_pct':'-1'}])
        self.assertEqual(r['earlier']['n'],2)
        self.assertEqual(r['later']['n'],1)
    def test_fail_bad_pair(self):
        with self.assertRaises(ValueError):analyze([{'symbol':'AB','date':'2026-10-01','net_pct':'1'}])
    def test_leave_one_out(self):
        r=analyze([{'symbol':'A:B','date':'2026-10-01','net_pct':'1'},{'symbol':'C:D','date':'2026-10-02','net_pct':'-1'}])
        self.assertEqual(r['leave_one_pair_out']['A:B']['mean_net_pct'],-1)
