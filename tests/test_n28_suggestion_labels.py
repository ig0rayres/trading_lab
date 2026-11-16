"""N28.1 — suggestion surfaces must stay labeled; rank tip alone cannot reach paper gateway."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from prodigy_paper_ingest import ingest
from trading_dashboard_data import (
    SUGGESTION_SURFACE_KEYS,
    command_panel,
    validate_command_panel_suggestions,
)
from v4_web_dashboard import build_snapshot, render_page


class N28SuggestionSurfaceTests(unittest.TestCase):
    def _write_prodigy_rank(self, root: Path) -> None:
        intel = root / 'intelligence'
        intel.mkdir(parents=True)
        payload = {
            'mode': 'PRODIGY_RANK_RESEARCH_ONLY',
            'as_of': '2026-11-16T12:00:00Z',
            'top_10_research': [
                {'provider': 'prov-a', 'status': 'watch', 'prodigy_score': 42},
            ],
        }
        (intel / 'prodigy-top10-latest.json').write_text(json.dumps(payload))

    def test_command_panel_suggestion_surfaces_self_check(self):
        with tempfile.TemporaryDirectory() as d:
            self._write_prodigy_rank(Path(d))
            cp = command_panel(d)
            self.assertTrue(cp['suggestion_policy']['self_check_ok'])
            self.assertEqual(cp['suggestion_policy']['surface_keys'], list(SUGGESTION_SURFACE_KEYS))
            violations = validate_command_panel_suggestions(cp)
            self.assertEqual(violations, [])
            for key in SUGGESTION_SURFACE_KEYS:
                surface = cp[key]
                self.assertEqual(surface['surface_kind'], 'suggestion')
                self.assertFalse(surface['paper_allowed'])
                self.assertFalse(surface['execution_authorized'])
                self.assertEqual(surface['orders_sent'], 0)

    def test_dashboard_html_exposes_suggestion_labels(self):
        with tempfile.TemporaryDirectory() as d:
            self._write_prodigy_rank(Path(d))
            page = render_page(build_snapshot(d))
            self.assertIn('research_tip', page)
            self.assertIn('sugestão', page.lower())

    def test_rank_row_without_ticket_blocks_before_paper_gateway(self):
        env = {
            'LIVE_TRADING_ENABLED': 'false',
            'SIGNAL_COPY_SECRET': 'test-secret',
        }
        rank_row = {'provider_id': 'prov-a', 'status': 'watch', 'prodigy_score': 1}
        with patch('prodigy_paper_ingest.process_after_gate_b') as mock_pg:
            result = ingest(rank_row, {}, env, dry_run=False, strategy_phase='research')
            mock_pg.assert_not_called()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result.get('reject_code'), 'TICKET_FIELDS_REQUIRED')
        self.assertEqual(result.get('orders_sent'), 0)


if __name__ == '__main__':
    unittest.main()