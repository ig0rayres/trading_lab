import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from evolution_engine import add_decision, review

class EvolutionEngineTests(unittest.TestCase):
    def test_review_tracks_preview_and_blocks_without_claiming_pnl(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'evolution'
            webhook = Path(tmp) / 'webhooks'
            webhook.mkdir()
            (webhook / 'journal.jsonl').write_text('\n'.join([
                json.dumps({'at': '2026-10-28T20:44:22Z', 'result': {'status': 'PREVIEW_ONLY', 'orders_sent': 0}}),
                json.dumps({'at': '2026-10-28T20:45:22Z', 'result': {'status': 'BLOCKED', 'reasons': ['RISK_CAP'], 'orders_sent': 0}})
            ])+'\n')
            add_decision(root / 'decisions.jsonl', {'at': '2026-10-28T20:42:00Z', 'signal_id': 's-000001', 'strategy_id': 'A', 'decision': 'REJECTED', 'reason':'NO_VOLUME'})
            report = review('2026-10-28', root, webhook)
            self.assertEqual(report['webhook_processed'], 2)
            self.assertEqual(report['decisions']['REJECTED'], 1)
            self.assertFalse(report['performance_metrics_available'])
            self.assertEqual(report['orders_sent'], 0)
    def test_rejects_invalid_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                add_decision(Path(tmp) / 'x.jsonl', {'at': '2026-10-28T20:00:00Z', 'signal_id': 'abc123', 'decision':'EXECUTE'})

if __name__ == '__main__': unittest.main()
