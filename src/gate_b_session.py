"""NYSE and B3 regular session gates shared by Gate A ingest and Gate B."""
from __future__ import annotations

from datetime import datetime, time, timezone


def market_from_signal(signal: dict) -> str:
    market = signal.get('market')
    if isinstance(market, str) and market.strip():
        return market.strip().upper()
    asset = str(signal.get('asset_class', 'us_equity')).lower()
    if asset == 'b3_equity':
        return 'B3_EQUITY'
    if asset == 'crypto':
        return 'CRYPTO'
    return 'US_EQUITY'


def within_regular_session(now=None) -> bool:
    from zoneinfo import ZoneInfo

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    from original import load_original

    ny = now.astimezone(ZoneInfo('America/New_York'))
    sess = load_original().entry.session(ny.date())
    if sess is None:
        return False
    open_t, close_t = sess
    t = ny.time()
    return open_t <= t <= close_t


def _b3_weekday_ok(day) -> bool:
    return day.weekday() < 5


def within_b3_session(now=None) -> bool:
    from zoneinfo import ZoneInfo

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    local = now.astimezone(ZoneInfo('America/Sao_Paulo'))
    if not _b3_weekday_ok(local.date()):
        return False
    open_t = time(10, 0)
    close_t = time(17, 55)
    cur = local.time()
    return open_t <= cur <= close_t


def within_market_session(now, market: str) -> bool:
    if market == 'CRYPTO':
        return True
    if market == 'B3_EQUITY':
        return within_b3_session(now)
    return within_regular_session(now)


def within_signal_session(signal: dict, now) -> bool:
    return within_market_session(now, market_from_signal(signal))
