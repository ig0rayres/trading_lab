"""N31.4 — G-AJUSTE guardrails: tips/forecast never paper; TimesFM fail-closed."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from evolution_engine import review
from timesfm_context import build_timesfm_block


class N31GAjusteGuardrails(unittest.TestCase):
    def test_review_never_imports_paper_gateway(self):
        src = (Path(__file__).resolve().parents[1] / 'src' / 'evolution_engine.py').read_text()
        self.assertNotIn('process_after_gate_b', src)
        self.assertNotIn('paper_gateway', src)

    def test_timesfm_missing_no_numeric_forecast_in_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'evolution'
            webhook = Path(tmp) / 'webhooks'
            webhook.mkdir()
            (webhook / 'journal.jsonl').write_text(
                json.dumps({'at': '2026-11-16T12:00:00Z', 'result': {'status': 'BLOCKED', 'orders_sent': 0}}) + '\n'
            )
            report = review('2026-11-16', root, webhook, context_providers=[])
            self.assertEqual(report['timesfm']['timesfm_status'], 'UNAVAILABLE')
            self.assertEqual(report['orders_sent'], 0)
            blob = json.dumps(report)
            self.assertNotIn('forecast_values', blob)
            for tip in report['tips']:
                self.assertIn(tip['label'], {'research_tip', 'suggestion', 'continuous_improvement'})
                self.assertFalse(tip['paper_allowed'])
                self.assertEqual(tip['orders_sent'], 0)

    def test_live_trading_invariant_in_run_sh(self):
        run_sh = (Path(__file__).resolve().parents[1] / 'scripts' / 'run.sh').read_text()
        self.assertIn('LIVE_TRADING_ENABLED', run_sh)

    def test_dockerfile_live_false(self):
        docker = (Path(__file__).resolve().parents[1] / 'Dockerfile').read_text()
        docker_l = docker.lower()
        self.assertTrue(
            'live_trading_enabled=false' in docker_l or 'live_trading_enabled: "false"' in docker_l,
            'Dockerfile must keep LIVE_TRADING_ENABLED false',
        )


if __name__ == '__main__':
    unittest.main()