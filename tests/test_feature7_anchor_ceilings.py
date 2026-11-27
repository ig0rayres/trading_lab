"""Feature 7 — named proofs that control_flags ceilings block with a reason (no order path)."""
import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).resolve().parents[1]
_VENDOR = _ROOT / 'vendor' / 'day-trader-skill'
_VENDOR_RISK = _VENDOR / 'trader-risk' / 'check.py'
if _VENDOR.is_dir():
    os.environ.setdefault('UPSTREAM_DIR', str(_VENDOR))


def _vendor_ready() -> bool:
    return _VENDOR_RISK.is_file()

sys.path.insert(0, str(_ROOT / 'src'))

import gate_b_risk as gb
from portfolio_risk_v4 import evaluate


def _signal(qty=1):
    return {
        'provider': 'tradingview',
        'signal_id': 'F7_ANCHOR',
        'symbol': 'AAPL',
        'side': 'buy',
        'asset_class': 'us_equity',
        'entry': '100',
        'stop': '99',
        'target': '102',
        'quantity': qty,
        'strategy_key': 'signal_copy',
    }


def _snapshot(**overrides):
    base = {
        'complete': True,
        'daily_pnl_verified': True,
        'weekly_pnl_verified': True,
        'broker_reconciled': True,
        'positions': [],
        'daily_pnl_brl': '0',
        'weekly_pnl_brl': '0',
        'available_cash_brl': '5000',
        'has_pending_orders': False,
    }
    base.update(overrides)
    return base


def _candidate(**overrides):
    base = {
        'market': 'US_EQUITY',
        'symbol': 'MSFT',
        'side': 'buy',
        'verified': True,
        'trading_mode': 'PAPER',
        'quantity': 1,
        'entry_brl': '100',
        'stop_brl': '99',
    }
    base.update(overrides)
    return base


class Feature7PortfolioAnchorTests(unittest.TestCase):
    def test_feature7_anchor_capital_limit_blocks(self):
        c = _candidate(quantity=100, entry_brl='60', stop_brl='59')
        s = _snapshot()
        reasons = evaluate(c, s)['reasons']
        self.assertIn('CAPITAL_LIMIT', reasons)

    def test_feature7_anchor_max_trade_risk_blocks(self):
        c = _candidate(quantity=20, entry_brl='40', stop_brl='37')
        s = _snapshot()
        self.assertIn('MAX_TRADE_RISK', evaluate(c, s)['reasons'])

    def test_feature7_anchor_aggregate_risk_blocks(self):
        c = _candidate(entry_brl='110', stop_brl='100')
        s = _snapshot(
            positions=[
                {
                    'market': 'US_EQUITY',
                    'symbol': 'NVDA',
                    'notional_brl': '3000',
                    'planned_risk_brl': '195',
                }
            ]
        )
        self.assertIn('AGGREGATE_RISK_LIMIT', evaluate(c, s)['reasons'])

    def test_feature7_anchor_max_positions_blocks(self):
        c = _candidate()
        s = _snapshot(
            positions=[
                {'market': 'US_EQUITY', 'symbol': 'A', 'notional_brl': '100', 'planned_risk_brl': '10'},
                {'market': 'US_EQUITY', 'symbol': 'B', 'notional_brl': '100', 'planned_risk_brl': '10'},
                {'market': 'US_EQUITY', 'symbol': 'C', 'notional_brl': '100', 'planned_risk_brl': '10'},
            ]
        )
        self.assertIn('MAX_POSITIONS', evaluate(c, s)['reasons'])

    def test_feature7_anchor_daily_loss_blocks(self):
        c = _candidate()
        s = _snapshot(daily_pnl_brl='-200')
        self.assertIn('DAILY_LOSS_HALT', evaluate(c, s)['reasons'])

    def test_feature7_anchor_weekly_loss_blocks(self):
        c = _candidate()
        s = _snapshot(weekly_pnl_brl='-500')
        self.assertIn('WEEKLY_LOSS_HALT', evaluate(c, s)['reasons'])


class Feature7GateBAnchorTests(unittest.TestCase):
    def test_feature7_anchor_gate_b_max_positions_blocks(self):
        self.assertEqual(
            gb.open_positions_cap_reached(
                [{'symbol': 'MSFT'}, {'symbol': 'GOOG'}, {'symbol': 'NVDA'}],
                cap=3,
            ),
            'MAX_POSITIONS',
        )

    def test_feature7_anchor_gate_b_kill_switch_blocks(self):
        with patch.dict(os.environ, {'TRADING_LAB_KILL_SWITCH': 'true'}, clear=False):
            self.assertTrue(gb.kill_switch_active())

    @unittest.skipUnless(_vendor_ready(), 'vendor/day-trader-skill checkout required')
    def test_feature7_anchor_gate_b_trade_risk_blocks(self):
        from original import load_original

        risk = load_original().risk
        now = risk.parse_now('2026-10-28 10:15')
        d = gb.evaluate_signed_signal(
            _signal(qty=100),
            fx=Decimal('5'),
            now=now,
            strategy_phase='paper_limited',
        )
        self.assertEqual(d['decision'], 'rejected')
        self.assertTrue(d['reject_code'])

    @unittest.skipUnless(_vendor_ready(), 'vendor/day-trader-skill checkout required')
    @patch('gate_b_risk.fetch_control_flags')
    def test_feature7_anchor_gate_b_tight_capital_config_blocks_large_ticket(self, mock_flags):
        from original import load_original

        mock_flags.return_value = {
            'capital_cents': 100_000,
            'max_risk_per_trade_cents': 5_000,
            'max_open_positions': 3,
            'max_aggregate_risk_cents': 20_000,
            'max_daily_loss_cents': 20_000,
            'max_weekly_loss_cents': 50_000,
            'prodigy_risk_cents': 2_000,
        }
        risk = load_original().risk
        now = risk.parse_now('2026-10-28 10:15')
        d = gb.evaluate_signed_signal(
            _signal(qty=50),
            fx=Decimal('5'),
            now=now,
            strategy_phase='paper_limited',
        )
        self.assertEqual(d['decision'], 'rejected')
        self.assertTrue(d['reject_code'])


if __name__ == '__main__':
    unittest.main()