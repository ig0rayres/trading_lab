"""NYSE regular session gate shared by Gate A ingest and Gate B."""
from __future__ import annotations

from datetime import datetime, timezone


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
