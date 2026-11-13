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
