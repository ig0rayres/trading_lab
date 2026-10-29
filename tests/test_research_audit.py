import csv
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, '/app/src' if Path('/app/src/research_audit.py').exists() else str(Path(__file__).resolve().parents[1] / 'src'))
from research_audit import inspect_report

class ResearchAuditTests(unittest.TestCase):
    def fixture(self, n, mean, pf):
        td = tempfile.TemporaryDirectory()
        folder = Path(td.name)
        stats = {'evaluations': n, 'mean_net_r': mean, 'profit_factor': pf}
        report = {'status': 'MULTISTRATEGY_EXPLORATORY_NOT_VALIDATED',
                  'total_evaluations': n,
                  'strategies': {'example': {'2.0R': {'all': stats,
                                                     'earlier_sessions': stats,
                                                     'later_sessions': stats}}}}
        (folder / 'summary.json').write_text(json.dumps(report))
        (folder / 'errors.json').write_text(json.dumps([{'reason': 'INSUFFICIENT_PAST_COMPLETE_SESSIONS'}]))
        with (folder / 'trades.csv').open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['strategy','target_r','date'])
            w.writeheader()
            for k in range(n):
                w.writerow({'strategy':'example','target_r':2.0,
                            'date':f'2026-09-{(k % 30) + 1:02d}'})
        return td, folder

    def test_tiny_positive_is_rejected(self):
        td, path = self.fixture(3,.257,1.71)
        with td:
            c = inspect_report(path)['candidates'][0]
            self.assertEqual(c['screen'], 'REJECT_FOR_NOW')
            self.assertIn('INSUFFICIENT_EVALUATIONS',c['reasons'])

    def test_large_negative_is_rejected(self):
        td, path = self.fixture(200,-.2,.6)
        with td:
            c = inspect_report(path)['candidates'][0]
            self.assertIn('NONPOSITIVE_NET_EXPECTANCY',c['reasons'])
            self.assertEqual(c['distinct_days'],30)

    def test_positive_not_live_approved(self):
        td, path = self.fixture(200,.2,1.3)
        with td:
            result=inspect_report(path)
            self.assertEqual(result['candidates'][0]['screen'],'NEEDS_INDEPENDENT_VALIDATION')
            self.assertEqual(result['promoted_to_live'],0)
            self.assertEqual(result['diagnostics_by_reason']['INSUFFICIENT_PAST_COMPLETE_SESSIONS'],1)

    def test_wrong_report_refused(self):
        td, path = self.fixture(3,.1,1.1)
        with td:
            (path/'summary.json').write_text('{"status":"OTHER"}')
            with self.assertRaises(ValueError):inspect_report(path)
