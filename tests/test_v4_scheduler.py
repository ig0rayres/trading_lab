import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from v4_scheduler import lock_once, run_cycle, record_status, invalidate_stale_manifest, main


class SchedulerTests(unittest.TestCase):
    def test_readonly_success(self):
        with patch.dict(os.environ, {'LIVE_TRADING_ENABLED': 'false'}):
            def mock(cmd, **kwargs):
                self.assertIn('v4_run_once.py', cmd[1]); self.assertNotIn('paper-gateway', cmd)
                return SimpleNamespace(returncode=0, stdout='research only')
            result = run_cycle('universe.json', '/tmp/reports', runner=mock)
            self.assertEqual(result['status'], 'FINISHED_RESEARCH')
            self.assertEqual(result['orders_sent'], 0)

    def test_failure_is_not_success(self):
        with patch.dict(os.environ, {'LIVE_TRADING_ENABLED': 'false'}):
            value = run_cycle('u', 'out', runner=lambda *a, **kw: SimpleNamespace(returncode=3, stdout='error'))
            self.assertEqual(value['status'], 'FAILED_OR_BLOCKED')

    def test_live_guard(self):
        with patch.dict(os.environ, {'LIVE_TRADING_ENABLED': 'true'}):
            self.assertEqual(run_cycle('u', 'out')['status'], 'BLOCKED_LIVE_FLAG')
            self.assertEqual(main(['--universe', 'u', '--output-dir', 'out', '--once']), 2)

    def test_lock_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / '.lock'
            fd = lock_once(p)
            try:
                with self.assertRaises(BlockingIOError):
                    lock_once(p)
                record_status(Path(tmp) / 'status.json', {'status': 'OK', 'orders_sent': 0})
                self.assertFalse(__import__('json').loads((Path(tmp) / 'status.json').read_text())['execution_authorized'])
            finally:
                os.close(fd)

    def test_failed_cycle_invalidates_previous_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / 'v4_manifest.json'
            manifest.write_text('{"status":"RESEARCH_ONLY"}')
            invalidate_stale_manifest(tmp, {'status': 'FAILED_OR_BLOCKED', 'exit_code': 2})
            self.assertFalse(manifest.exists())

    def test_success_keeps_current_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / 'v4_manifest.json'
            manifest.write_text('{"status":"RESEARCH_ONLY"}')
            invalidate_stale_manifest(tmp, {'status': 'FINISHED_RESEARCH', 'exit_code': 0})
            self.assertTrue(manifest.exists())

    def test_manifest_symlink_is_never_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'target'
            target.write_text('preserve')
            (Path(tmp) / 'v4_manifest.json').symlink_to(target)
            with self.assertRaises(ValueError):
                invalidate_stale_manifest(tmp, {'status': 'CYCLE_TIMEOUT', 'exit_code': 124})
            self.assertEqual(target.read_text(), 'preserve')

    def test_lock_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / '.lock'; p.symlink_to(Path(tmp) / 'target')
            with self.assertRaises(ValueError):
                lock_once(p)

if __name__ == '__main__':
    unittest.main()
