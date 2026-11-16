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
            paper = Path(tmp) / 'paper'
            paper.mkdir()
            (paper / 'order-snapshots.jsonl').write_text(
                json.dumps({
                    'at': '2026-10-28T20:46:00Z',
                    'client_order_id': 'cid-fill-1',
                    'status': 'MONITORED',
                    'broker_fill_confirmed': True,
                    'strategy_key': 'A',
                }) + '\n',
                encoding='utf-8',
            )
            report = review('2026-10-28', root, webhook, context_providers=[])
            self.assertEqual(report['webhook_processed'], 2)
            self.assertEqual(report['decisions']['REJECTED'], 1)
            self.assertFalse(report['performance_metrics_available'])
            self.assertEqual(report['orders_sent'], 0)
            self.assertEqual(report['changes_applied'], 0)
            self.assertGreaterEqual(report['execution_summary']['fills_observed'], 1)
            self.assertGreaterEqual(report['execution_summary']['non_fills_observed'], 1)
            labels = {t['label'] for t in report['tips']}
            self.assertTrue(labels.intersection({'research_tip', 'suggestion'}))
            for tip in report['tips']:
                self.assertFalse(tip.get('execution_authorized', False))
                self.assertEqual(tip.get('orders_sent', 0), 0)
    def test_rejects_invalid_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                add_decision(Path(tmp) / 'x.jsonl', {'at': '2026-10-28T20:00:00Z', 'signal_id': 'abc123', 'decision':'EXECUTE'})

if __name__ == '__main__': unittest.main()
