import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import gate_b_risk as gb


def _signal(qty=1, entry='100', stop='99', target='102'):
    return {
        'provider': 'tradingview',
        'signal_id': 'RISK_TEST_001',
        'symbol': 'AAPL',
        'side': 'buy',
        'asset_class': 'us_equity',
        'entry': entry,
        'stop': stop,
        'target': target,
        'quantity': qty,
    }


class GateBRiskTest(unittest.TestCase):
    def setUp(self):
        from original import load_original

        self.risk = load_original().risk
        self.now = self.risk.parse_now('2026-10-28 10:15')
        self.fx = Decimal('5')

    def test_within_risk_passes(self):
        d = gb.evaluate_signed_signal(_signal(), fx=self.fx, now=self.now)
        self.assertEqual(d['decision'], 'paper_allowed')
        self.assertIsNone(d['reject_code'])

    def test_exceeds_brl50_risk_blocked(self):
        d = gb.evaluate_signed_signal(_signal(qty=100), fx=self.fx, now=self.now)
        self.assertEqual(d['decision'], 'rejected')
        self.assertTrue(d['reject_code'])

    def test_kill_switch_env(self):
        with patch.dict(os.environ, {'TRADING_LAB_KILL_SWITCH': 'true'}, clear=False):
            d = gb.evaluate_signed_signal(_signal(), fx=self.fx, now=self.now)
        self.assertEqual(d['reject_code'], 'KILL_SWITCH')


if __name__ == '__main__':
    unittest.main()
