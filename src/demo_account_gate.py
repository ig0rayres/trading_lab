"""G-MKT fail-closed: demo-panel markets need operator-named account path in env."""
import os

NO_DEMO_ACCOUNT_PATH = 'NO_DEMO_ACCOUNT_PATH'

DEMO_PANEL_MARKETS = frozenset({'B3_EQUITY', 'CRYPTO', 'FOREX'})

_DEMO_PATH_ENV = {
    'B3_EQUITY': 'DEMO_ACCOUNT_PATH_B3_EQUITY',
    'CRYPTO': 'DEMO_ACCOUNT_PATH_CRYPTO',
    'FOREX': 'DEMO_ACCOUNT_PATH_FOREX',
}


def named_demo_account_configured(market: str) -> bool:
    env_key = _DEMO_PATH_ENV.get(market)
    if not env_key:
        return True
    path = os.environ.get(env_key, '').strip()
    if not path:
        return False
    if market not in ('B3_EQUITY', 'FOREX'):
        return True
    from demo_broker_adapters import credentials_block_for_adapter

    blocked, _ = credentials_block_for_adapter(path, dict(os.environ))
    return not blocked


def demo_market_block_reason(market: str) -> str | None:
    if market not in DEMO_PANEL_MARKETS:
        return None
    if named_demo_account_configured(market):
        return None
    return NO_DEMO_ACCOUNT_PATH
