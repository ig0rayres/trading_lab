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
