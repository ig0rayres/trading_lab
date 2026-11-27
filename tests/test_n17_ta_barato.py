import json
import tempfile
import unittest
from pathlib import Path

from trading_dashboard_data import command_panel
from v4_web_dashboard import build_snapshot, render_page
from strategy_catalog import UPSTREAM_FORMULA_BLOCKED_KEYS, upstream_formula_blocked


class N17UpstreamFormulaTests(unittest.TestCase):
    def test_g_form_blocked_keys(self):
        self.assertIn('ta_barato', UPSTREAM_FORMULA_BLOCKED_KEYS)
        self.assertIn('momentum', UPSTREAM_FORMULA_BLOCKED_KEYS)
        self.assertTrue(upstream_formula_blocked('ta_barato'))
        self.assertFalse(upstream_formula_blocked('signal_copy'))

    def test_command_panel_ta_barato_shadow_not_run(self):
        with tempfile.TemporaryDirectory() as d:
            cp = command_panel(d)
            tb = cp['ta_barato_shadow']
            self.assertEqual(tb['upstream_formula'], 'BLOCKED')
            self.assertFalse(tb.get('paper_authorized'))
            self.assertEqual(tb['status'], 'NOT_RUN')

    def test_command_panel_loads_shadow_report(self):
        with tempfile.TemporaryDirectory() as d:
            research = Path(d) / 'research'
            research.mkdir()
            payload = {
                'schema_version': 'opportunity-v4',
                'mode': 'SHADOW_ONLY',
                'orders_sent': 0,
                'opportunities': [
                    {
                        'market': 'US_EQUITY',
                        'symbol': 'AAPL',
                        'mode': 'SHADOW_ONLY',
                        'drop_pct_from_previous_5_bar_peak': 6.2,
                        'radar_candidate': True,
                        'paper_approved': False,
                    }
                ],
            }
            (research / 'opportunities-latest.json').write_text(json.dumps(payload))
            tb = command_panel(d)['ta_barato_shadow']
            self.assertEqual(tb['status'], 'OK')
            self.assertEqual(len(tb['items']), 1)
            self.assertEqual(tb['items'][0]['symbol'], 'AAPL')

    def test_dashboard_html_includes_ta_barato_section(self):
        with tempfile.TemporaryDirectory() as d:
            data = build_snapshot(d)
            page = render_page(data)
            self.assertIn('ta_barato', page)
            self.assertIn('Tá Barato', page)


if __name__ == '__main__':
    unittest.main()