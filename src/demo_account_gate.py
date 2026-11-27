"""G-MKT fail-closed: demo-panel markets need operator-named account path in env."""
import os

NO_DEMO_ACCOUNT_PATH = 'NO_DEMO_ACCOUNT_PATH'

DEMO_PANEL_MARKETS = frozenset({'B3_EQUITY', 'CRYPTO', 'FOREX'})

_DEMO_PATH_ENV = {
    'B3_EQUITY': 'DEMO_ACCOUNT_PATH_B3_EQUITY',
    'CRYPTO': 'DEMO_ACCOUNT_PATH_CRYPTO',
    'FOREX': 'DEMO_ACCOUNT_PATH_FOREX',
}


def _demo_path_value(market: str, env: dict[str, str] | None) -> str:
    env_key = _DEMO_PATH_ENV.get(market)
    if not env_key:
        return ''
    if env is not None:
        return (env.get(env_key) or os.environ.get(env_key) or '').strip()
    return os.environ.get(env_key, '').strip()


def named_demo_account_configured(market: str, env: dict[str, str] | None = None) -> bool:
    env_key = _DEMO_PATH_ENV.get(market)
    if not env_key:
        return True
    path = _demo_path_value(market, env)
    if not path:
        return False
    if market == 'CRYPTO':
        from demo_broker_adapters import G_MKT_ADAPTER_PATH_ALPACA_PAPER

        return path == G_MKT_ADAPTER_PATH_ALPACA_PAPER
    if market not in ('B3_EQUITY', 'FOREX'):
        return True
    from demo_broker_adapters import credentials_block_for_adapter

    merged = {**os.environ, **(env or {})}
    blocked, _ = credentials_block_for_adapter(path, merged)
    return not blocked


def demo_market_block_reason(market: str, env: dict[str, str] | None = None) -> str | None:
    if market not in DEMO_PANEL_MARKETS:
        return None
    if named_demo_account_configured(market, env):
        return None
    return NO_DEMO_ACCOUNT_PATH


_PRESENCE_ENV_KEYS = (
    'CLEAR_SIM_BASE_URL',
    'CLEAR_SIM_API_KEY',
    'CLEAR_SIM_API_SECRET',
    'OANDA_PRACTICE_API_TOKEN',
    'OANDA_PRACTICE_ACCOUNT_ID',
    'DEMO_ACCOUNT_PATH_B3_EQUITY',
    'DEMO_ACCOUNT_PATH_FOREX',
)

_PRESENCE_MARKETS = ('B3_EQUITY', 'FOREX')


def _presence_merged_env(env: dict[str, str] | None) -> dict[str, str]:
    if env is None:
        return dict(os.environ)
    return {**os.environ, **env}


def _env_key_present(name: str, merged: dict[str, str]) -> bool:
    return bool((merged.get(name) or '').strip())


def _live_trading_enabled_false(merged: dict[str, str]) -> bool:
    raw = (merged.get('LIVE_TRADING_ENABLED') or '').strip().lower()
    if not raw:
        return True
    return raw in ('false', '0', 'no')


def env_presence_report(env: dict[str, str] | None = None) -> dict:
    """Names-only env smoke: present/absent keys and B3/FOREX gate status (no values, no HTTP)."""
    merged = _presence_merged_env(env)
    keys = {
        name: 'present' if _env_key_present(name, merged) else 'absent'
        for name in _PRESENCE_ENV_KEYS
    }
    markets: dict[str, str] = {}
    for market in _PRESENCE_MARKETS:
        block = demo_market_block_reason(market, env)
        markets[market] = 'READY' if block is None else NO_DEMO_ACCOUNT_PATH
    return {
        'keys': keys,
        'markets': markets,
        'live_trading_enabled_false': _live_trading_enabled_false(merged),
    }
