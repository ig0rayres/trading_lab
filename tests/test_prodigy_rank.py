import json
import sys
import tempfile
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from prodigy_rank import calculate

class ProdigyTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.base=Path(self.t.name)
        self.now=datetime(2026,10,28,tzinfo=timezone.utc)
    def write(self, id, profits, error='200', weeks=5):
        trades=[]
        for i,p in enumerate(profits):
            date=self.now-timedelta(days=2+(i%weeks)*2)
            trades.append({'CloseDate':date.isoformat(),'ProfitLoss':p})
        (self.base/f'{id}_closed_trades.json').write_text(json.dumps({'strategy_id':str(id),'dataset':'closed_trades','raw':{'ResponseStatus':{'ErrorCode':error},'Results':trades}}))
    def test_perfect_short_streak_not_approved(self):
        self.write(1,[100]*5)
        p=calculate(self.base,self.now)['providers'][0]
        self.assertLess(p['shrunk_win_rate_pct'],100)
        self.assertFalse(p['copy_approved'])
    def test_better_candidate_emerges_without_30_trades(self):
        self.write(1,[100]*10, weeks=5)
        p=calculate(self.base,self.now)['providers'][0]
        self.assertEqual(p['status'],'PRODIGY_CANDIDATE_RESEARCH')
        self.assertFalse(calculate(self.base,self.now)['execution_authorized'])
    def test_broken_api_fails_closed(self):
        self.write(1,[100]*10,error='500')
        self.assertEqual(calculate(self.base,self.now)['providers'][0]['status'],'UNSCORABLE')
    def test_old_trades_are_not_ranked(self):
        self.write(1,[100]*10)
        d=json.loads((self.base/'1_closed_trades.json').read_text())
        for t in d['raw']['Results']:t['CloseDate']=(self.now-timedelta(days=190)).isoformat()
        (self.base/'1_closed_trades.json').write_text(json.dumps(d))
        self.assertEqual(calculate(self.base,self.now)['providers'][0]['closed_trades_15d'],0)
