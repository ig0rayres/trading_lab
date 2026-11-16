"""N30.1 — operational risk snapshot refresh from ledger + Alpaca paper GET."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import risk_snapshot_refresh as rsr
from risk_control_flags import TIGHT_DEFAULTS, brl_from_cents


def _ledger_snapshot(**overrides):
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


class RiskSnapshotRefreshTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / 'risk.json'
        self.env = {
            'LIVE_TRADING_ENABLED': 'false',
            'ALPACA_PAPER_TRADE': 'true',
            'ALPACA_BASE_URL': 'https://paper-api.alpaca.markets',
            'ALPACA_API_KEY': 'test',
            'ALPACA_SECRET_KEY': 'test',
            'USD_BRL_REFERENCE': '5',
            'V4_RISK_SNAPSHOT_FILE': str(self.out),
        }

    def test_merge_writes_fresh_snapshot_with_counts(self):
        positions = [{'symbol': 'AAPL', 'side': 'long', 'market_value': '100'}]
        orders = [{'id': 'ord-1', 'status': 'new'}]

        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {}
            if 'positions' in endpoint:
                return positions
            return orders

        with patch.object(rsr, 'portfolio_risk_snapshot', return_value=_ledger_snapshot()):
            result = rsr.refresh_once(self.env, broker_get=getter)
        self.assertEqual(result['status'], 'REFRESHED')
        self.assertTrue(self.out.is_file())
        data = json.loads(self.out.read_text())
        self.assertEqual(data['alpaca_positions_count'], 1)
        self.assertEqual(data['alpaca_open_orders_count'], 1)
        self.assertIn('at_utc', data)
        self.assertTrue(data['daily_pnl_verified'])
        stamp = datetime.fromisoformat(data['at_utc'].replace('Z', '+00:00'))
        self.assertLess(abs((datetime.now(timezone.utc) - stamp).total_seconds()), 5)

    def test_ledger_failure_writes_nothing(self):
        def getter(endpoint, env):
            return [] if 'positions' in endpoint else []

        def broken_ledger(**kwargs):
            raise OSError('ledger unavailable')

        with patch.object(rsr, 'portfolio_risk_snapshot', side_effect=broken_ledger):
            result = rsr.refresh_once(self.env, broker_get=getter)
        self.assertEqual(result['status'], 'SKIPPED')
        self.assertFalse(self.out.exists())

    def test_alpaca_failure_writes_nothing(self):
        def broken(endpoint, env):
            raise TimeoutError('alpaca down')

        with patch.object(rsr, 'portfolio_risk_snapshot', return_value=_ledger_snapshot()):
            result = rsr.refresh_once(self.env, broker_get=broken)
        self.assertEqual(result['status'], 'SKIPPED')
        self.assertFalse(self.out.exists())

    def test_planned_risk_brl_uses_per_trade_anchor(self):
        anchor_brl = str(brl_from_cents(int(TIGHT_DEFAULTS['max_risk_per_trade_cents'])))
        raw = [
            {
                'symbol': 'AAPL',
                'side': 'long',
                'asset_class': 'us_equity',
                'market_value': '100',
            },
            {
                'symbol': 'MSFT',
                'side': 'long',
                'asset_class': 'us_equity',
                'market_value': '200',
            },
        ]
        fx = Decimal('5')
        normalized = rsr._normalize_positions(raw, fx, anchor_brl)
        self.assertEqual(len(normalized), 2)
        for row in normalized:
            self.assertEqual(row['planned_risk_brl'], anchor_brl)
        self.assertEqual(Decimal(anchor_brl), Decimal('50'))
        aggregate = sum(Decimal(p['planned_risk_brl']) for p in normalized)
        self.assertEqual(aggregate, Decimal(anchor_brl) * 2)

    def test_refresh_once_applies_anchor_planned_risk_to_positions(self):
        anchor_brl = str(brl_from_cents(int(TIGHT_DEFAULTS['max_risk_per_trade_cents'])))
        positions = [
            {
                'symbol': 'AAPL',
                'side': 'long',
                'asset_class': 'us_equity',
                'market_value': '100',
            },
            {
                'symbol': 'BTCUSD',
                'side': 'long',
                'asset_class': 'crypto',
                'market_value': '50',
            },
        ]

        def getter(endpoint, env):
            if 'positions' in endpoint:
                return positions
            return []

        with patch.object(rsr, 'portfolio_risk_snapshot', return_value=_ledger_snapshot()):
            rsr.refresh_once(self.env, broker_get=getter)
        data = json.loads(self.out.read_text())
        risks = [Decimal(p['planned_risk_brl']) for p in data['positions']]
        self.assertEqual(risks, [Decimal(anchor_brl), Decimal(anchor_brl)])
        self.assertEqual(sum(risks), Decimal(anchor_brl) * 2)

    def test_main_exit_nonzero_when_skipped(self):
        env = dict(self.env, V4_RISK_SNAPSHOT_FILE='')
        with patch.dict(os.environ, env, clear=False):
            code = rsr.main([])
        self.assertEqual(code, 1)

    def test_unverified_pnl_not_marked_complete(self):
        def getter(endpoint, env):
            return [] if 'positions' in endpoint or 'orders' in endpoint else {}

        snap = _ledger_snapshot(
            complete=False,
            daily_pnl_verified=False,
            weekly_pnl_verified=False,
            broker_reconciled=False,
        )
        with patch.object(rsr, 'portfolio_risk_snapshot', return_value=snap):
            rsr.refresh_once(self.env, broker_get=getter)
        data = json.loads(self.out.read_text())
        self.assertFalse(data['complete'])
        self.assertFalse(data['daily_pnl_verified'])


if __name__ == '__main__':
    unittest.main()