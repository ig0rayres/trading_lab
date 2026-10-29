import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from overnight_research import simulation,positions

class OvernightResearchTests(unittest.TestCase):
    def setUp(self):
        self.rows=[{'date':f'2026-01-{i:02d}','open':100+i,'close':101+i} for i in range(1,9)]
    def test_all_strategies(self):
        for name in ['long_cash','cash_long','cash_reversal','reversal_cash','long_reversal','long_long']:
            self.assertEqual(len(simulation(self.rows,name,2)),6)
    def test_cost_reduces_returns(self):
        for name in ['long_cash','cash_long','cash_reversal','reversal_cash','long_reversal','long_long']:
            a=simulation(self.rows,name,2);b=simulation(self.rows,name,10)
            self.assertLess(sum(z['net_return'] for z in b),sum(z['net_return'] for z in a))
    def test_day_reversal_uses_same_night(self):
        self.assertEqual(positions('cash_reversal',0.03,-0.02),(0,1))
        self.assertEqual(positions('cash_reversal',0.03,0.02),(0,-1))
    def test_night_reversal_uses_prior_day(self):
        self.assertEqual(positions('reversal_cash',-0.01,0.03),(1,0))
    def test_no_empty_profit(self):
        self.assertEqual(simulation([], 'long_cash',2),[])
