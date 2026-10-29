import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from time_machine_audit import choose
class TimeMachineAuditTests(unittest.TestCase):
 def test_selects_target(self):
  rows=[{'date':'2026-10-20','symbol':'A','target_r':'1'}, {'date':'2026-10-19','symbol':'B','target_r':'2'}, {'date':'2026-10-21','symbol':'C','target_r':'2'}]
  self.assertEqual([x['symbol'] for x in choose(rows,1,2)],['C'])
 def test_empty(self):
  self.assertEqual(choose([],3,2),[])
if __name__=='__main__':unittest.main()
