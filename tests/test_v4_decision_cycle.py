import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from src.v4_decision_cycle import run, main

NOW = datetime(2026, 10, 29, 16, tzinfo=timezone.utc)
CYCLE = {'automatic_order_submission': False, 'usable_for_live_trading': False,
         'results': {}, 'errors': {}}
NEWS = {'mode': 'NEWS_FIRST_INTERNAL_SIMULATION', 'authorized_to_trade': False,
        'orders_sent': 0, 'signals': [{'symbol': 'AAPL', 'article_id': 'x',
        'decision': 'NO_TRADE', 'research_status': 'EVIDENCE_PENDING', 'quantity': 0,
        'blocker_reasons': ['SOURCE_UNVERIFIED']}]}

class TestDecisionCycle(unittest.TestCase):
    def test_integrates_news_and_empty_market(self):
        out = run(CYCLE, NEWS, now=NOW)
        self.assertEqual(len(out['decisions']), 1)
        self.assertEqual(out['scanned_markets'], 0)
        self.assertEqual(out['orders_sent'], 0)
        self.assertFalse(out['paper_approved'])
        self.assertEqual(out['status'], 'RESEARCH_ONLY')

    def test_upstream_errors_propagate(self):
        cycle = dict(CYCLE, errors={'B3_EQUITY:ITUB4': 'API_UNAVAILABLE'})
        out = run(cycle, now=NOW)
        self.assertEqual(out['status'], 'PARTIAL_OR_BLOCKED')
        self.assertEqual(out['market_cycle_errors']['B3_EQUITY:ITUB4'], 'API_UNAVAILABLE')

    def test_unsafe_cycle_rejected(self):
        with self.assertRaises(ValueError):
            run(dict(CYCLE, automatic_order_submission=True), now=NOW)

    def test_unsafe_news_rejected(self):
        with self.assertRaises(ValueError):
            run(CYCLE, dict(NEWS, authorized_to_trade=True), now=NOW)

    def test_cli_writes_provenance_and_no_orders(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root, 'market.json'); source.write_text(json.dumps(CYCLE))
            news = Path(root, 'news.json'); news.write_text(json.dumps(NEWS))
            dest = Path(root, 'decisions.json')
            with patch.dict(os.environ, {'LIVE_TRADING_ENABLED': 'false'}):
                self.assertEqual(main(['--market-cycle', str(source), '--news', str(news), '--output', str(dest)]), 0)
            out = json.loads(dest.read_text())
            self.assertEqual(out['orders_sent'], 0)
            self.assertEqual(out['decisions'][0]['kind'], 'NEWS_REVIEW')

    def test_cli_optional_risk_preview_is_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root, 'market.json'); source.write_text(json.dumps(CYCLE))
            news = Path(root, 'news.json'); news.write_text(json.dumps(NEWS))
            output = Path(root, 'decisions.json'); risk = Path(root, 'risk.json')
            with patch.dict(os.environ, {'LIVE_TRADING_ENABLED': 'false'}):
                self.assertEqual(main(['--market-cycle', str(source), '--news', str(news),
                                       '--output', str(output), '--risk-output', str(risk)]), 0)
            preview = json.loads(risk.read_text())
            self.assertEqual(preview['orders_sent'], 0)
            self.assertEqual(preview['results'][0]['risk_preview'], 'BLOCKED')
            self.assertIn('RESEARCH_SIGNAL_NOT_EXECUTION_AUTHORIZED', preview['results'][0]['reasons'])

    def test_cli_refuses_same_risk_and_decision_path(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root, 'market.json'); source.write_text(json.dumps(CYCLE))
            output = Path(root, 'output.json')
            with patch.dict(os.environ, {'LIVE_TRADING_ENABLED': 'false'}):
                self.assertEqual(main(['--market-cycle', str(source), '--output', str(output),
                                       '--risk-output', str(output)]), 2)
            self.assertFalse(output.exists())

    def test_cli_live_flag_blocks_output(self):
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root, 'result.json')
            with patch.dict(os.environ, {'LIVE_TRADING_ENABLED': 'true'}):
                self.assertEqual(main(['--market-cycle', 'missing', '--output', str(dest)]), 2)
            self.assertFalse(dest.exists())

if __name__ == '__main__': unittest.main()
