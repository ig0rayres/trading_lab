"""Momentum and ta_barato signals from upstream find_setups only. No broker calls."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

from internal_signal_producer import emit_internal_signal, plan_levels_from_close
from original import load_original
from risk_control_flags import fetch_control_flags

MOMENTUM_SETUPS = frozenset({'breakout_20d', 'bull_flag', 'reclaim_ma20'})
TA_BARATO_SETUPS = frozenset({'oversold', 'oversold_bounce'})
ASSUMPTION_LABEL = 'ASSUMPTION_OPERATOR_REVIEW'
_MIN_CLOSES = 30


def load_producer_universe(path: Path | None = None) -> list[tuple[str, str]]:
    root = path or Path(os.environ.get('UNIVERSE_FILE', '/app/config/universe.json'))
    if not root.is_file():
        root = Path(__file__).resolve().parents[1] / 'config' / 'universe.json'
    rows = json.loads(root.read_text(encoding='utf-8'))
    out: list[tuple[str, str]] = []
    for row in rows:
        market = str(row.get('market', '')).upper()
        symbol = str(row.get('symbol', '')).upper()
        if market in ('US_EQUITY', 'CRYPTO') and symbol:
            out.append((market, symbol))
    return out


def _closes_from_bars(bars: list[dict[str, Any]], close_key: str) -> list[float]:
    return [float(b[close_key]) for b in bars if b.get(close_key) is not None]


def _bar_date_from_feed(market: str, row: dict[str, Any]) -> str:
    bars = row.get('bars') or []
    if not bars:
        return datetime.now(timezone.utc).date().isoformat()
    last = bars[-1]
    key = 'at_utc' if market == 'US_EQUITY' else 'at_utc'
    stamp = str(last.get(key, ''))[:10]
    return stamp or datetime.now(timezone.utc).date().isoformat()


def _asset_class_for_market(market: str) -> str:
    return 'crypto' if market == 'CRYPTO' else 'us_equity'


def _matching_strategies(tags: set[str]) -> list[str]:
    keys: list[str] = []
    if tags & MOMENTUM_SETUPS:
        keys.append('momentum')
    if tags & TA_BARATO_SETUPS:
        keys.append('ta_barato')
    return keys


def _emit_one_family(
    orig: Any,
    *,
    strategy_key: str,
    symbol: str,
    asset_class: str,
    bar_date: str,
    entry_price: float,
    fx: Decimal,
    flags: dict[str, Any],
    queue: Path | None,
    now: datetime,
    secret: str | None,
    setup_tags: list[str],
) -> dict[str, Any]:
    levels = plan_levels_from_close(
        orig,
        symbol=symbol,
        entry_price=entry_price,
        bar_date=bar_date,
        fx=fx,
        flags=flags,
        asset_class=asset_class,
    )
    if not levels:
        return {'symbol': symbol, 'strategy_key': strategy_key, 'status': 'SKIP_SIZE', 'orders_sent': 0}
    result = emit_internal_signal(
        strategy_key=strategy_key,
        symbol=symbol,
        asset_class=asset_class,
        bar_date=bar_date,
        levels=levels,
        queue=queue,
        now=now,
        secret=secret,
    )
    result['symbol'] = symbol
    result['strategy_key'] = strategy_key
    result['setup_tags'] = setup_tags
    result['assumption'] = ASSUMPTION_LABEL
    return result


def _scan_symbol(
    orig: Any,
    *,
    market: str,
    symbol: str,
    closes: list[float],
    bar_date: str,
    fx: Decimal,
    flags: dict[str, Any],
    queue: Path | None,
    now: datetime,
    secret: str | None,
) -> list[dict[str, Any]]:
    if len(closes) < _MIN_CLOSES:
        return []
    tags, _nums = orig.scanner.find_setups(closes)
    tag_set = set(tags)
    asset_class = _asset_class_for_market(market)
    setup_tags = sorted(tag_set)
    keys = _matching_strategies(tag_set)
    return [
        _emit_one_family(
            orig,
            strategy_key=key,
            symbol=symbol,
            asset_class=asset_class,
            bar_date=bar_date,
            entry_price=closes[-1],
            fx=fx,
            flags=flags,
            queue=queue,
            now=now,
            secret=secret,
            setup_tags=setup_tags,
        )
        for key in keys
    ]


def _collect_closes(
    market: str,
    symbol: str,
    *,
    equity_fetch: Callable[..., dict],
    crypto_fetch: Callable[..., dict],
) -> tuple[list[float], str]:
    if market == 'CRYPTO':
        row = crypto_fetch(symbol=symbol, interval='1d')
        return _closes_from_bars(row.get('bars') or [], 'close_brl'), _bar_date_from_feed(market, row)
    row = equity_fetch(market=market, symbol=symbol, interval='1d', period='3mo')
    return _closes_from_bars(row.get('bars') or [], 'close'), _bar_date_from_feed(market, row)


def run_once(
    *,
    orig: Any | None = None,
    universe: list[tuple[str, str]] | None = None,
    equity_fetch: Callable[..., dict] | None = None,
    crypto_fetch: Callable[..., dict] | None = None,
    fx: Decimal | None = None,
    queue: Path | None = None,
    now: datetime | None = None,
    secret: str | None = None,
    conn_factory: Callable | None = None,
) -> dict[str, Any]:
    if os.environ.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        return {'status': 'BLOCKED', 'reason': 'LIVE_FORBIDDEN', 'orders_sent': 0, 'signals': []}
    when = now or datetime.now(timezone.utc)
    orig = orig or load_original()
    from paper_audit import amount

    rate = fx if fx is not None else amount(os.environ.get('USD_BRL_REFERENCE', '5'))
    flags = fetch_control_flags(conn_factory=conn_factory)
    pairs = universe if universe is not None else load_producer_universe()
    if equity_fetch is None:
        from v4_equity_feed import fetch_public_candles as equity_fetch
    if crypto_fetch is None:
        from v4_crypto_feed import fetch_public_candles as crypto_fetch
    q = queue or Path(os.environ.get('TV_QUEUE_DIR', '/app/reports/webhooks/pending'))
    results: list[dict[str, Any]] = []
    errors: dict[str, str] = {}
    for market, symbol in pairs:
        key = f'{market}:{symbol}'
        try:
            closes, bar_date = _collect_closes(market, symbol, equity_fetch=equity_fetch, crypto_fetch=crypto_fetch)
            results.extend(
                _scan_symbol(
                    orig,
                    market=market,
                    symbol=symbol,
                    closes=closes,
                    bar_date=bar_date,
                    fx=rate,
                    flags=flags,
                    queue=q,
                    now=when,
                    secret=secret,
                )
            )
        except Exception as exc:
            errors[key] = f'{type(exc).__name__}: {exc}'
    orders = sum(1 for r in results if r.get('status') == 'QUEUED')
    return {
        'status': 'RESEARCH_ONLY',
        'generated_at_utc': when.isoformat(),
        'signals': results,
        'errors': errors,
        'orders_sent': 0,
        'queued': orders,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Scanner family internal signal producer')
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--output', default='')
    args = parser.parse_args(argv)
    report = run_once()
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text + '\n', encoding='utf-8')
    print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())