"""N29 — TDD for G-MKT demo broker adapters (Clear B3, OANDA Practice, wiring).

Spec: docs/ROADMAP.md Sprint N29, docs/REQUIREMENTS.md v0.4 Feature 7 G-MKT.
RED gate: `demo_broker_adapters` + extended wiring on `DEMO_ACCOUNT_PATH_*` env keys.
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from demo_account_gate import (  # noqa: E402
    NO_DEMO_ACCOUNT_PATH,
    demo_market_block_reason,
    env_presence_report,
    named_demo_account_configured,
)
from demo_broker_adapters import (  # noqa: E402
    DEMO_ACCOUNT_PATH_ENV_BY_MARKET,
    G_MKT_ADAPTER_PATH_ALPACA_PAPER,
    G_MKT_ADAPTER_PATH_CLEAR_SIMULATED,
    G_MKT_ADAPTER_PATH_OANDA_PRACTICE,
    OANDA_PRACTICE_API_HOST,
    adapter_path_for_market,
    build_demo_adapter,
    credentials_block_for_adapter,
)

NO_DEMO_ACCOUNT_REJECT = NO_DEMO_ACCOUNT_PATH
ALPACA_PAPER_HOST = 'https://paper-api.alpaca.markets'
OANDA_LIVE_HOST = 'https://api-fxtrade.oanda.com'

MOCK_CLEAR_ORDER_ID = 'clear-sim-order-n29'
MOCK_OANDA_ORDER_ID = 'oanda-practice-order-n29'


def _clear_env_with_path() -> dict[str, str]:
    return {
        'LIVE_TRADING_ENABLED': 'false',
        'DEMO_ACCOUNT_PATH_B3_EQUITY': G_MKT_ADAPTER_PATH_CLEAR_SIMULATED,
        'CLEAR_SIM_BASE_URL': 'https://simulator.clear.example',
        'CLEAR_SIM_API_KEY': 'test-clear-key',
        'CLEAR_SIM_API_SECRET': 'test-clear-secret',
    }


def _oanda_env_with_path() -> dict[str, str]:
    return {
        'LIVE_TRADING_ENABLED': 'false',
        'DEMO_ACCOUNT_PATH_FOREX': G_MKT_ADAPTER_PATH_OANDA_PRACTICE,
        'OANDA_PRACTICE_API_TOKEN': 'practice-token-value',
        'OANDA_PRACTICE_ACCOUNT_ID': 'practice-account-id',
    }


def _wiring_env() -> dict[str, str]:
    return {
        'LIVE_TRADING_ENABLED': 'false',
        'DEMO_ACCOUNT_PATH_B3_EQUITY': G_MKT_ADAPTER_PATH_CLEAR_SIMULATED,
        'DEMO_ACCOUNT_PATH_CRYPTO': G_MKT_ADAPTER_PATH_ALPACA_PAPER,
        'DEMO_ACCOUNT_PATH_FOREX': G_MKT_ADAPTER_PATH_OANDA_PRACTICE,
    }


class ClearSimulatedAdapterTests(unittest.TestCase):
    def test_clear_simulated_mock_http_exposes_position_open_order_and_fill_status(self):
        env = _clear_env_with_path()
        adapter = build_demo_adapter(G_MKT_ADAPTER_PATH_CLEAR_SIMULATED, env)
        calls: list[str] = []

        def fake_urlopen(req: Request, timeout=None):  # noqa: ARG001
            calls.append(req.full_url)
            self.assertNotIn(ALPACA_PAPER_HOST, req.full_url)
            if req.method == 'GET' and '/positions' in req.full_url:
                payload = [{'symbol': 'ITUB4', 'qty': '100', 'side': 'long'}]
            elif req.method == 'GET' and '/orders' in req.full_url and 'open' in req.full_url:
                payload = [{'order_id': MOCK_CLEAR_ORDER_ID, 'status': 'open', 'symbol': 'ITUB4'}]
            elif req.method == 'POST':
                payload = {'order_id': MOCK_CLEAR_ORDER_ID, 'status': 'accepted'}
            elif req.method == 'GET' and MOCK_CLEAR_ORDER_ID in req.full_url:
                payload = {
                    'order_id': MOCK_CLEAR_ORDER_ID,
                    'status': 'filled',
                    'filled_qty': '100',
                }
            else:
                raise HTTPError(req.full_url, 404, 'not found', hdrs=None, fp=None)
            return _JsonResponse(payload)

        with patch('demo_broker_adapters.urlopen', side_effect=fake_urlopen):
            submit = adapter.submit_order(symbol='ITUB4', side='buy', quantity=100)
            positions = adapter.list_positions()
            open_orders = adapter.list_open_orders()
            final = adapter.get_order_status(MOCK_CLEAR_ORDER_ID)

        self.assertEqual(submit['broker_order_id'], MOCK_CLEAR_ORDER_ID)
        self.assertEqual(submit['status'], 'accepted')
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['symbol'], 'ITUB4')
        self.assertEqual(open_orders[0]['order_id'], MOCK_CLEAR_ORDER_ID)
        self.assertEqual(final['status'], 'filled')
        self.assertTrue(calls)
        for url in calls:
            self.assertNotIn('paper-api.alpaca.markets', url)

    def test_clear_simulated_without_credentials_blocks_no_demo_account_path(self):
        env = {'DEMO_ACCOUNT_PATH_B3_EQUITY': G_MKT_ADAPTER_PATH_CLEAR_SIMULATED}
        blocked, reason = credentials_block_for_adapter(G_MKT_ADAPTER_PATH_CLEAR_SIMULATED, env)
        self.assertTrue(blocked)
        self.assertEqual(reason, NO_DEMO_ACCOUNT_REJECT)
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(demo_market_block_reason('B3_EQUITY'), NO_DEMO_ACCOUNT_REJECT)


class OandaPracticeAdapterTests(unittest.TestCase):
    def test_oanda_practice_uses_practice_host_only_order_and_fill(self):
        env = _oanda_env_with_path()
        adapter = build_demo_adapter(G_MKT_ADAPTER_PATH_OANDA_PRACTICE, env)
        hosts: list[str] = []

        def fake_urlopen(req: Request, timeout=None):  # noqa: ARG001
            hosts.append(req.host)
            self.assertEqual(req.host, 'api-fxpractice.oanda.com')
            self.assertNotEqual(req.host, 'api-fxtrade.oanda.com')
            if req.method == 'POST' and '/orders' in req.full_url:
                payload = {
                    'orderCreateTransaction': {'id': MOCK_OANDA_ORDER_ID, 'type': 'MARKET_ORDER'},
                }
            elif req.method == 'GET' and 'transactions' in req.full_url:
                payload = {
                    'transactions': [
                        {
                            'id': 'fill-1',
                            'orderID': MOCK_OANDA_ORDER_ID,
                            'type': 'ORDER_FILL',
                            'units': '1000',
                        }
                    ]
                }
            else:
                raise HTTPError(req.full_url, 404, 'not found', hdrs=None, fp=None)
            return _JsonResponse(payload)

        with patch('demo_broker_adapters.urlopen', side_effect=fake_urlopen):
            created = adapter.submit_order(symbol='EUR_USD', side='buy', quantity=1000)
            fill = adapter.get_fill_for_order(MOCK_OANDA_ORDER_ID)

        self.assertEqual(created['broker_order_id'], MOCK_OANDA_ORDER_ID)
        self.assertEqual(fill['type'], 'ORDER_FILL')
        self.assertTrue(OANDA_PRACTICE_API_HOST.startswith('https://api-fxpractice.oanda.com'))
        self.assertTrue(all(h == 'api-fxpractice.oanda.com' for h in hosts))
        self.assertTrue(all(OANDA_LIVE_HOST not in h for h in hosts))

    def test_oanda_practice_empty_token_blocks_with_reason(self):
        env = {
            'DEMO_ACCOUNT_PATH_FOREX': G_MKT_ADAPTER_PATH_OANDA_PRACTICE,
            'OANDA_PRACTICE_API_TOKEN': '',
            'OANDA_PRACTICE_ACCOUNT_ID': 'practice-account-id',
        }
        blocked, reason = credentials_block_for_adapter(G_MKT_ADAPTER_PATH_OANDA_PRACTICE, env)
        self.assertTrue(blocked)
        self.assertEqual(reason, NO_DEMO_ACCOUNT_REJECT)


class N27AlpacaOnlyDemoPathGateTests(unittest.TestCase):
    """N27 partial: only CRYPTO may name Alpaca paper; B3/FOREX stay fail-closed."""

    def test_n27_crypto_without_named_path_not_configured(self):
        env = {'LIVE_TRADING_ENABLED': 'false'}
        with patch.dict(os.environ, env, clear=True):
            self.assertFalse(named_demo_account_configured('CRYPTO'))
            self.assertEqual(demo_market_block_reason('CRYPTO'), NO_DEMO_ACCOUNT_REJECT)

    def test_n27_crypto_only_alpaca_paper_path_counts_as_configured(self):
        env = {
            'LIVE_TRADING_ENABLED': 'false',
            'DEMO_ACCOUNT_PATH_CRYPTO': G_MKT_ADAPTER_PATH_ALPACA_PAPER,
        }
        with patch.dict(os.environ, env, clear=True):
            self.assertTrue(named_demo_account_configured('CRYPTO'))
            self.assertIsNone(demo_market_block_reason('CRYPTO'))

    def test_n27_crypto_non_alpaca_named_path_fail_closed(self):
        """Alpaca-only loop: Clear/OANDA paths must not unlock CRYPTO demo send."""
        env = {
            'LIVE_TRADING_ENABLED': 'false',
            'DEMO_ACCOUNT_PATH_CRYPTO': G_MKT_ADAPTER_PATH_CLEAR_SIMULATED,
        }
        with patch.dict(os.environ, env, clear=True):
            self.assertFalse(named_demo_account_configured('CRYPTO'))
            self.assertEqual(demo_market_block_reason('CRYPTO'), NO_DEMO_ACCOUNT_REJECT)


class DemoAccountPathWiringTests(unittest.TestCase):
    def test_named_path_env_selects_g_mkt_adapter_per_market(self):
        env = _wiring_env()
        self.assertEqual(
            adapter_path_for_market('B3_EQUITY', env),
            G_MKT_ADAPTER_PATH_CLEAR_SIMULATED,
        )
        self.assertEqual(
            adapter_path_for_market('CRYPTO', env),
            G_MKT_ADAPTER_PATH_ALPACA_PAPER,
        )
        self.assertEqual(
            adapter_path_for_market('FOREX', env),
            G_MKT_ADAPTER_PATH_OANDA_PRACTICE,
        )
        self.assertEqual(
            DEMO_ACCOUNT_PATH_ENV_BY_MARKET['B3_EQUITY'],
            'DEMO_ACCOUNT_PATH_B3_EQUITY',
        )
        self.assertEqual(
            DEMO_ACCOUNT_PATH_ENV_BY_MARKET['CRYPTO'],
            'DEMO_ACCOUNT_PATH_CRYPTO',
        )
        self.assertEqual(
            DEMO_ACCOUNT_PATH_ENV_BY_MARKET['FOREX'],
            'DEMO_ACCOUNT_PATH_FOREX',
        )
        with patch.dict(os.environ, {**env, **_clear_env_with_path()}, clear=True):
            self.assertTrue(named_demo_account_configured('B3_EQUITY'))
        with patch.dict(os.environ, {**env, **_oanda_env_with_path()}, clear=True):
            self.assertTrue(named_demo_account_configured('FOREX'))
        clear_adapter = build_demo_adapter(
            adapter_path_for_market('B3_EQUITY', env),
            _clear_env_with_path(),
        )
        oanda_adapter = build_demo_adapter(
            adapter_path_for_market('FOREX', env),
            _oanda_env_with_path(),
        )
        self.assertEqual(clear_adapter.adapter_path, G_MKT_ADAPTER_PATH_CLEAR_SIMULATED)
        self.assertEqual(oanda_adapter.adapter_path, G_MKT_ADAPTER_PATH_OANDA_PRACTICE)

    def test_regression_b3_forex_adapter_http_never_posts_alpaca_paper(self):
        """ADR-010 / N29.4: demo adapters for B3 and FOREX must not target Alpaca paper."""
        for path, env in (
            (G_MKT_ADAPTER_PATH_CLEAR_SIMULATED, _clear_env_with_path()),
            (G_MKT_ADAPTER_PATH_OANDA_PRACTICE, _oanda_env_with_path()),
        ):
            adapter = build_demo_adapter(path, env)
            urls: list[str] = []

            def fake_urlopen(req: Request, timeout=None):  # noqa: ARG001
                urls.append(req.full_url)
                if path == G_MKT_ADAPTER_PATH_CLEAR_SIMULATED and req.method == 'POST':
                    return _JsonResponse({'order_id': MOCK_CLEAR_ORDER_ID, 'status': 'accepted'})
                if path == G_MKT_ADAPTER_PATH_OANDA_PRACTICE and req.method == 'POST':
                    return _JsonResponse(
                        {'orderCreateTransaction': {'id': MOCK_OANDA_ORDER_ID}}
                    )
                raise HTTPError(req.full_url, 404, 'not found', hdrs=None, fp=None)

            with patch('demo_broker_adapters.urlopen', side_effect=fake_urlopen):
                adapter.submit_order(symbol='DEMO', side='buy', quantity=1)
            self.assertTrue(urls)
            for url in urls:
                self.assertNotIn('paper-api.alpaca.markets', url)


class EnvPresenceReportTests(unittest.TestCase):
    """N35 — per-key presence smoke without exposing secret values or HTTP."""

    _SECRET_MARKERS = ('test-clear-secret', 'practice-token-value')

    def test_n35_empty_env_all_keys_absent_markets_blocked_live_false(self):
        with patch.dict(os.environ, {'LIVE_TRADING_ENABLED': 'false'}, clear=True):
            report = env_presence_report()
        for name in (
            'CLEAR_SIM_BASE_URL',
            'CLEAR_SIM_API_KEY',
            'CLEAR_SIM_API_SECRET',
            'OANDA_PRACTICE_API_TOKEN',
            'OANDA_PRACTICE_ACCOUNT_ID',
            'DEMO_ACCOUNT_PATH_B3_EQUITY',
            'DEMO_ACCOUNT_PATH_FOREX',
        ):
            self.assertEqual(report['keys'][name], 'absent')
        self.assertEqual(report['markets']['B3_EQUITY'], NO_DEMO_ACCOUNT_PATH)
        self.assertEqual(report['markets']['FOREX'], NO_DEMO_ACCOUNT_PATH)
        self.assertTrue(report['live_trading_enabled_false'])

    def test_n35_full_mock_creds_keys_present_markets_ready(self):
        env = {**_clear_env_with_path(), **_oanda_env_with_path()}
        with patch.dict(os.environ, env, clear=True):
            report = env_presence_report()
        for name in report['keys']:
            self.assertEqual(report['keys'][name], 'present', name)
        self.assertEqual(report['markets']['B3_EQUITY'], 'READY')
        self.assertEqual(report['markets']['FOREX'], 'READY')
        self.assertTrue(report['live_trading_enabled_false'])

    def test_n35_missing_one_clear_key_that_name_absent_b3_blocked(self):
        env = _clear_env_with_path()
        del env['CLEAR_SIM_API_SECRET']
        with patch.dict(os.environ, env, clear=True):
            report = env_presence_report()
        self.assertEqual(report['keys']['CLEAR_SIM_API_SECRET'], 'absent')
        self.assertEqual(report['keys']['CLEAR_SIM_API_KEY'], 'present')
        self.assertEqual(report['markets']['B3_EQUITY'], NO_DEMO_ACCOUNT_PATH)

    def test_n35_report_repr_and_json_contain_no_fixture_secrets(self):
        env = {**_clear_env_with_path(), **_oanda_env_with_path()}
        with patch.dict(os.environ, env, clear=True):
            report = env_presence_report()
        blob = repr(report) + json.dumps(report)
        for marker in self._SECRET_MARKERS:
            self.assertNotIn(marker, blob)

    def test_n35_urlopen_raise_report_still_returns_no_http(self):
        def boom(*_args, **_kwargs):
            raise RuntimeError('urlopen must not be called')

        with patch.dict(os.environ, {}, clear=True):
            with patch('demo_broker_adapters.urlopen', side_effect=boom):
                report = env_presence_report()
        self.assertIn('keys', report)
        self.assertIn('markets', report)

    def test_n35_live_trading_true_live_trading_enabled_false_is_false(self):
        env = {
            **_clear_env_with_path(),
            **_oanda_env_with_path(),
            'LIVE_TRADING_ENABLED': 'true',
        }
        with patch.dict(os.environ, env, clear=True):
            with patch('demo_broker_adapters.urlopen', side_effect=RuntimeError('no http')):
                report = env_presence_report()
        self.assertFalse(report['live_trading_enabled_false'])
        blob = repr(report) + json.dumps(report)
        for marker in self._SECRET_MARKERS:
            self.assertNotIn(marker, blob)


class _JsonResponse:
    """Minimal urllib response stub for adapter HTTP mocks."""

    def __init__(self, payload: dict | list):
        self._raw = json.dumps(payload).encode('utf-8')

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


if __name__ == '__main__':
    unittest.main()
