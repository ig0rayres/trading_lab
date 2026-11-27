"""Ops helper: refresh V4 risk snapshot from mocked Alpaca GETs."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import risk_snapshot_refresh as rsr


def _env() -> dict[str, str]:
    return {
        'LIVE_TRADING_ENABLED': 'false',
        'ALPACA_PAPER_TRADE': 'true',
        'ALPACA_BASE_URL': 'https://paper-api.alpaca.markets',
        'ALPACA_API_KEY': 'test-key',
        'ALPACA_SECRET_KEY': 'test-secret',
        'USD_BRL_REFERENCE': '5',
    }


class RiskSnapshotRefreshTests(unittest.TestCase):
    def test_build_snapshot_sets_fresh_counts_and_at_utc(self):
        fixed = datetime(2026, 11, 16, 12, 0, 0, tzinfo=timezone.utc)

        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status': 'ACTIVE', 'currency': 'USD', 'cash': '1000'}
            if endpoint.endswith('positions'):
                return [
                    {
                        'symbol': 'AAPL',
                        'side': 'long',
                        'asset_class': 'us_equity',
                        'market_value': '200',
                    }
                ]
            return [{'id': 'ord-1'}]

        snap = rsr.build_refresh_snapshot(_env(), getter=getter, now=fixed)
        self.assertEqual(snap['at_utc'], fixed.isoformat())
        self.assertEqual(snap['alpaca_positions_count'], 1)
        self.assertEqual(snap['alpaca_open_orders_count'], 1)
        self.assertEqual(snap['positions'][0]['market'], 'US_EQUITY')
        self.assertEqual(snap['positions'][0]['symbol'], 'AAPL')
        self.assertEqual(snap['has_pending_orders'], True)
        self.assertEqual(snap['orders_sent'], 0)

    def test_refresh_to_file_atomic_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'risk-snapshot.json'
            out.write_text(
                json.dumps(
                    {
                        'positions': [
                            {
                                'market': 'US_EQUITY',
                                'symbol': 'AAPL',
                                'notional_brl': '1000',
                                'planned_risk_brl': '25',
                            }
                        ]
                    }
                )
            )

            def getter(endpoint, env):
                if endpoint.endswith('account'):
                    return {'cash': '500'}
                if endpoint.endswith('positions'):
                    return [
                        {
                            'symbol': 'AAPL',
                            'side': 'long',
                            'asset_class': 'us_equity',
                            'market_value': '100',
                        }
                    ]
                return []

            data = rsr.refresh_to_file(_env(), out, getter=getter)
            loaded = json.loads(out.read_text())
            self.assertEqual(loaded['alpaca_positions_count'], 1)
            self.assertEqual(loaded['positions'][0]['planned_risk_brl'], '25')
            self.assertEqual(data['schema_version'], rsr.SCHEMA_VERSION)

    def test_maybe_auto_refresh_skips_when_flag_false(self):
        with patch.object(rsr, 'refresh_to_file') as mock_refresh:
            self.assertFalse(
                rsr.maybe_auto_refresh_risk_snapshot(
                    {'RISK_SNAPSHOT_AUTO_REFRESH': 'false', 'V4_RISK_SNAPSHOT_FILE': '/tmp/x.json'}
                )
            )
            mock_refresh.assert_not_called()

    def test_maybe_auto_refresh_calls_when_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'snap.json'

            def getter(endpoint, env):
                if endpoint.endswith('account'):
                    return {'cash': '100'}
                return []

            env = {**_env(), 'RISK_SNAPSHOT_AUTO_REFRESH': 'true', 'V4_RISK_SNAPSHOT_FILE': str(target)}
            self.assertTrue(rsr.maybe_auto_refresh_risk_snapshot(env, getter=getter))
            self.assertTrue(target.exists())

    @patch('risk_snapshot_refresh.maybe_auto_refresh_risk_snapshot')
    def test_process_after_gate_b_invokes_auto_refresh_hook(self, mock_refresh):
        import paper_gateway_queue as pgq

        mock_refresh.return_value = True
        env = {
            'PAPER_SIGNAL_AUTO_ENABLED': 'true',
            'PAPER_EXECUTION_ENABLED': 'true',
            'PAPER_SIGNAL_ACCOUNT_ACK': 'I_AUTHORIZE_ALPACA_PAPER_ONLY',
        }
        decision = {'decision': 'paper_allowed', 'reject_code': None}

        def broker_run(_signal, _env, ledger=None):
            return {'status': 'QUEUED', 'orders_sent': 0}

        signal = {
            'provider': 'tradingview',
            'signal_id': 'refresh-hook',
            'symbol': 'AAPL',
            'side': 'buy',
            'entry': 100,
            'stop': 99,
            'target': 102,
            'quantity': 1,
        }
        with patch('risk_control_flags.demo_send_allowed', return_value=(False, 'DEMO_OPERATION_OFF')):
            pgq.process_after_gate_b(signal, decision, env, broker_run=broker_run)
        mock_refresh.assert_called_once_with(env)


if __name__ == '__main__':
    unittest.main()