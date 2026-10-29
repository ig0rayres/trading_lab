import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from multistrategy import previous_level, STRATEGIES
class MultiStrategyTests(unittest.TestCase):
    def test_all_strategies_declared(self):
        self.assertEqual(len(STRATEGIES),8)
    def test_no_future_lookahead(self):
        import datetime as d
        dates=[d.date(2026,10,20),d.date(2026,10,21),d.date(2026,10,22)]
        completed={dates[0]:[{'high':100}],dates[1]:[{'high':105}],dates[2]:[{'high':999}]}
        self.assertEqual(previous_level(completed,dates[2],2),105)
    def test_insufficient_sessions(self):
        import datetime as d
        self.assertIsNone(previous_level({d.date(2026,10,20):[{'high':100}]},d.date(2026,10,21),20))
if __name__=='__main__':unittest.main()
