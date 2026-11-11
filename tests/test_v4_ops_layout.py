import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]


class V4OpsLayoutTests(unittest.TestCase):
    def test_run_sh_exposes_v4_ops_command(self):
        run_sh = _REPO / 'scripts' / 'run.sh'
        if not run_sh.is_file():
            self.skipTest('run.sh missing')
        text = run_sh.read_text(encoding='utf-8')
        self.assertIn('v4-ops)', text)

    def test_ops_main_supervises_dashboard(self):
        ops = _REPO / 'scripts' / 'v4_ops_main.sh'
        if not ops.is_file():
            self.skipTest('v4_ops_main.sh missing')
        body = ops.read_text(encoding='utf-8')
        self.assertIn('v4-dashboard', body)
        self.assertIn('v4-scheduler', body)
        self.assertIn('DASHBOARD_AUTOSTART', body)
        self.assertIn('tv-worker', body)
        self.assertIn('TV_WORKER_AUTOSTART', body)
        self.assertIn('TV_WORKER_INTERVAL_SEC', body)

    def test_worker_supervisor_does_not_replace_scheduler_exec(self):
        ops = _REPO / 'scripts' / 'v4_ops_main.sh'
        if not ops.is_file():
            self.skipTest('v4_ops_main.sh missing')
        lines = ops.read_text(encoding='utf-8').splitlines()
        exec_lines = [ln for ln in lines if ln.startswith('exec ')]
        self.assertEqual(len(exec_lines), 1)
        self.assertIn('v4-scheduler', exec_lines[0])
        worker_lines = [ln for ln in lines if 'tv-worker' in ln]
        self.assertTrue(any('|| true' in ln for ln in worker_lines))

    def test_dockerfile_default_is_v4_ops(self):
        dockerfile = _REPO / 'Dockerfile'
        if not dockerfile.is_file():
            self.skipTest('Dockerfile missing')
        docker = dockerfile.read_text(encoding='utf-8')
        self.assertIn('CMD ["v4-ops"', docker)


if __name__ == '__main__':
    unittest.main()
