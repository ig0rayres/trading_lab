"""G-MKT demo broker adapters (Clear simulated B3, OANDA practice FOREX, Alpaca crypto)."""
from __future__ import annotations

import json
import os
from typing import Any, Callable
from urllib.request import Request, urlopen

from demo_account_gate import NO_DEMO_ACCOUNT_PATH

G_MKT_ADAPTER_PATH_CLEAR_SIMULATED = 'clear_smart_trader_simulated'
G_MKT_ADAPTER_PATH_ALPACA_PAPER = 'alpaca_paper'
G_MKT_ADAPTER_PATH_OANDA_PRACTICE = 'oanda_fxtrade_practice'

OANDA_PRACTICE_API_HOST = 'https://api-fxpractice.oanda.com'

DEMO_ACCOUNT_PATH_ENV_BY_MARKET: dict[str, str] = {
    'B3_EQUITY': 'DEMO_ACCOUNT_PATH_B3_EQUITY',
    'CRYPTO': 'DEMO_ACCOUNT_PATH_CRYPTO',
    'FOREX': 'DEMO_ACCOUNT_PATH_FOREX',
}

_ALPACA_PAPER_HOST = 'https://paper-api.alpaca.markets'


def _env_get(env: dict[str, str], key: str) -> str:
    return (env.get(key) or os.environ.get(key) or '').strip()


def _live_trading_blocked(env: dict[str, str]) -> bool:
    raw = _env_get(env, 'LIVE_TRADING_ENABLED') or 'false'
    return raw.lower() not in ('false', '0', 'no', '')


def _resolve_opener(opener: Callable[..., Any] | None) -> Callable[..., Any]:
    return opener if opener is not None else urlopen


def _http_json(
    method: str,
    url: str,
    *,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    opener: Callable[..., Any] | None = None,
) -> Any:
    data = None
    hdrs = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode('utf-8')
        hdrs.setdefault('Content-Type', 'application/json')
    req = Request(url, data=data, headers=hdrs, method=method)
    with _resolve_opener(opener)(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def adapter_path_for_market(market: str, env: dict[str, str]) -> str:
    key = DEMO_ACCOUNT_PATH_ENV_BY_MARKET.get(market)
    if not key:
        return ''
    return _env_get(env, key)


def credentials_block_for_adapter(adapter_path: str, env: dict[str, str]) -> tuple[bool, str | None]:
    if adapter_path == G_MKT_ADAPTER_PATH_CLEAR_SIMULATED:
        missing = not all(
            _env_get(env, k)
            for k in ('CLEAR_SIM_BASE_URL', 'CLEAR_SIM_API_KEY', 'CLEAR_SIM_API_SECRET')
        )
    elif adapter_path == G_MKT_ADAPTER_PATH_OANDA_PRACTICE:
        missing = not _env_get(env, 'OANDA_PRACTICE_API_TOKEN') or not _env_get(
            env, 'OANDA_PRACTICE_ACCOUNT_ID'
        )
    elif adapter_path == G_MKT_ADAPTER_PATH_ALPACA_PAPER:
        missing = False
    else:
        missing = True
    if missing:
        return True, NO_DEMO_ACCOUNT_PATH
    return False, None


class _ClearSimulatedAdapter:
    def __init__(self, env: dict[str, str], opener: Callable[..., Any] | None = None) -> None:
        self.adapter_path = G_MKT_ADAPTER_PATH_CLEAR_SIMULATED
        self._env = env
        self._opener = opener
        base = _env_get(env, 'CLEAR_SIM_BASE_URL').rstrip('/')
        self._base = base
        self._headers = {
            'X-API-Key': _env_get(env, 'CLEAR_SIM_API_KEY'),
            'X-API-Secret': _env_get(env, 'CLEAR_SIM_API_SECRET'),
        }

    def submit_order(self, *, symbol: str, side: str, quantity: int | float) -> dict[str, Any]:
        if _live_trading_blocked(self._env):
            raise RuntimeError('LIVE_TRADING_ENABLED')
        payload = _http_json(
            'POST',
            f'{self._base}/orders',
            body={'symbol': symbol, 'side': side, 'quantity': quantity},
            headers=self._headers,
            opener=self._opener,
        )
        return {
            'broker_order_id': payload['order_id'],
            'status': payload.get('status', 'accepted'),
        }

    def list_positions(self) -> list[dict[str, Any]]:
        payload = _http_json('GET', f'{self._base}/positions', headers=self._headers, opener=self._opener)
        return list(payload) if isinstance(payload, list) else []

    def list_open_orders(self) -> list[dict[str, Any]]:
        payload = _http_json(
            'GET',
            f'{self._base}/orders/open',
            headers=self._headers,
            opener=self._opener,
        )
        return list(payload) if isinstance(payload, list) else []

    def get_order_status(self, order_id: str) -> dict[str, Any]:
        return _http_json(
            'GET',
            f'{self._base}/orders/{order_id}',
            headers=self._headers,
            opener=self._opener,
        )


class _OandaPracticeAdapter:
    def __init__(self, env: dict[str, str], opener: Callable[..., Any] | None = None) -> None:
        self.adapter_path = G_MKT_ADAPTER_PATH_OANDA_PRACTICE
        self._env = env
        self._opener = opener
        self._account_id = _env_get(env, 'OANDA_PRACTICE_ACCOUNT_ID')
        self._token = _env_get(env, 'OANDA_PRACTICE_API_TOKEN')
        self._headers = {'Authorization': f'Bearer {self._token}'}

    def submit_order(self, *, symbol: str, side: str, quantity: int | float) -> dict[str, Any]:
        if _live_trading_blocked(self._env):
            raise RuntimeError('LIVE_TRADING_ENABLED')
        units = str(int(quantity) if side == 'buy' else -int(quantity))
        url = f'{OANDA_PRACTICE_API_HOST}/v3/accounts/{self._account_id}/orders'
        payload = _http_json(
            'POST',
            url,
            body={'order': {'type': 'MARKET', 'instrument': symbol, 'units': units}},
            headers=self._headers,
            opener=self._opener,
        )
        tx = payload.get('orderCreateTransaction') or {}
        return {'broker_order_id': tx.get('id', ''), 'status': 'accepted'}

    def get_fill_for_order(self, order_id: str) -> dict[str, Any]:
        url = (
            f'{OANDA_PRACTICE_API_HOST}/v3/accounts/{self._account_id}'
            f'/transactions?orderID={order_id}'
        )
        payload = _http_json('GET', url, headers=self._headers, opener=self._opener)
        txs = payload.get('transactions') or []
        if not txs:
            raise KeyError('no fill transaction')
        return dict(txs[0])


class _AlpacaPaperAdapter:
    def __init__(self, env: dict[str, str], opener: Callable[..., Any] | None = None) -> None:
        self.adapter_path = G_MKT_ADAPTER_PATH_ALPACA_PAPER
        self._env = env
        self._opener = opener

    def submit_order(self, *, symbol: str, side: str, quantity: int | float) -> dict[str, Any]:
        if _live_trading_blocked(self._env):
            raise RuntimeError('LIVE_TRADING_ENABLED')
        url = f'{_ALPACA_PAPER_HOST}/v2/orders'
        payload = _http_json(
            'POST',
            url,
            body={'symbol': symbol, 'side': side, 'qty': str(quantity), 'type': 'market'},
            opener=self._opener,
        )
        return {'broker_order_id': payload.get('id', ''), 'status': payload.get('status', 'accepted')}


def build_demo_adapter(
    adapter_path: str,
    env: dict[str, str],
    *,
    opener: Callable[..., Any] | None = None,
):
    if adapter_path == G_MKT_ADAPTER_PATH_CLEAR_SIMULATED:
        return _ClearSimulatedAdapter(env, opener=opener)
    if adapter_path == G_MKT_ADAPTER_PATH_OANDA_PRACTICE:
        return _OandaPracticeAdapter(env, opener=opener)
    if adapter_path == G_MKT_ADAPTER_PATH_ALPACA_PAPER:
        return _AlpacaPaperAdapter(env, opener=opener)
    raise ValueError(f'unknown demo adapter path: {adapter_path!r}')
