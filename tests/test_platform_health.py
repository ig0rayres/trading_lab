import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from platform_health import (
    aggregate_overall,
    health_snapshot_path,
    load_health_snapshot,
    probe_queue,
    probe_webhook,
    run_probes,
    write_worker_stamp,
    worker_stamp_path,
)


class PlatformHealthTests(unittest.TestCase):
    def test_aggregate_overall_down_beats_degraded(self):
        components = [
            {'status': 'ok'},
            {'status': 'degraded'},
            {'status': 'down'},
        ]
        self.assertEqual(aggregate_overall(components), 'down')

    def test_webhook_skipped_without_url(self):
        with patch.dict(os.environ, {}, clear=True):
            result = probe_webhook({})
        self.assertEqual(result['status'], 'skipped')

    def test_run_probes_writes_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.dict(os.environ, {}, clear=True):
                payload = run_probes(root, {})
            path = health_snapshot_path(root)
            self.assertTrue(path.is_file())
            loaded = load_health_snapshot(root)
            self.assertEqual(loaded['schema_version'], 'platform-health-1')
            self.assertEqual(payload['overall'], loaded['overall'])

    def test_worker_stamp_enables_ok_worker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_worker_stamp(root, processed=2)
            self.assertTrue(worker_stamp_path(root).is_file())
            with patch.dict(os.environ, {'PLATFORM_HEALTH_WORKER_MAX_SEC': '9999'}, clear=False):
                from platform_health import probe_worker

                result = probe_worker(root)
            self.assertEqual(result['status'], 'ok')

    def test_stale_queue_degraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pending = root / 'pending'
            pending.mkdir()
            old = pending / 'x.json'
            old.write_text('{}', encoding='utf-8')
            import time

            os.utime(old, (time.time() - 7200, time.time() - 7200))
            with patch.dict(
                os.environ,
                {'TV_QUEUE_DIR': str(pending), 'PLATFORM_HEALTH_QUEUE_STALE_SEC': '60'},
                clear=False,
            ):
                result = probe_queue(root)
            self.assertEqual(result['status'], 'degraded')


class BuildSnapshotHealthTest(unittest.TestCase):
    def test_build_snapshot_includes_platform_health(self):
        import v4_web_dashboard as dash

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'paper').mkdir(parents=True, exist_ok=True)
            run_probes(root, {})
            data = dash.build_snapshot(root)
            self.assertIn('platform_health', data)
            self.assertEqual(data['platform_health']['schema_version'], 'platform-health-1')


if __name__ == '__main__':
    unittest.main()