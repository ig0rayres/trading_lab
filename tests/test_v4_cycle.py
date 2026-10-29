import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from v4_cycle import cycle

class V4CycleTests(unittest.TestCase):
    def test_safe_without_data(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'LIVE_TRADING_ENABLED':'false'}):
            x=cycle(d, runner=lambda *a,**kw: subprocess.CompletedProcess(a,0,'',''))
            self.assertEqual(x['status'],'OK_RESEARCH_ONLY')
            self.assertEqual([v['job'] for v in x['jobs']],['dashboard'])
            self.assertEqual(x['orders_sent'],0)
            self.assertFalse(x['paper_approved'])
            self.assertTrue((Path(d)/'research'/'v4-cycle-latest.json').exists())
    def test_both_existing_research_paths(self):
        with tempfile.TemporaryDirectory() as d:
            x=cycle(d, opportunity_input=Path(d)/'bars.json', news=True,
                    runner=lambda *a,**kw: subprocess.CompletedProcess(a,0,'',''))
            self.assertEqual([v['job'] for v in x['jobs']], ['opportunity_scan','news_first','dashboard'])
    def test_failure_is_not_success(self):
        with tempfile.TemporaryDirectory() as d:
            x=cycle(d, news=True, runner=lambda cmd, **kw: subprocess.CompletedProcess(cmd,2,'','bad data'))
            self.assertEqual(x['status'],'PARTIAL_OR_BLOCKED')
            self.assertEqual(x['orders_sent'],0)
    def test_live_enabled_hard_block(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(os.environ, {'LIVE_TRADING_ENABLED':'true'}):
            with self.assertRaisesRegex(ValueError,'LIVE_TRADING_NOT_DISABLED'):cycle(d)
            self.assertFalse((Path(d)/'research'/'v4-cycle-latest.json').exists())

if __name__=='__main__': unittest.main()
