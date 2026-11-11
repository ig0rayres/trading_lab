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
    return bool(os.environ.get(env_key, '').strip())


def demo_market_block_reason(market: str) -> str | None:
    if market not in DEMO_PANEL_MARKETS:
        return None
    if named_demo_account_configured(market):
        return None
    return NO_DEMO_ACCOUNT_PATH
