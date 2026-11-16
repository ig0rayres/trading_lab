"""Refresh V4_RISK_SNAPSHOT_FILE from ledger P&L + Alpaca paper GET counts. No order POST."""
from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from ledger_loss_anchor import portfolio_risk_snapshot
from paper_audit import amount, get_json, validate_env
from risk_control_flags import brl_from_cents, fetch_control_flags

_LOG = logging.getLogger(__name__)


def _normalize_positions(
    raw: list[Any],
    fx,
    planned_risk_brl: str,
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for p in raw:
        if not isinstance(p, dict) or p.get('side') != 'long':
            continue
        symbol = str(p.get('symbol', '')).strip().upper()
        if not symbol:
            continue
        asset = p.get('asset_class')
        market = {'us_equity': 'US_EQUITY', 'crypto': 'CRYPTO'}.get(asset)
        if market is None:
            continue
        value = amount(p.get('market_value', '0'))
        if value <= 0:
            continue
        out.append({
            'market': market,
            'symbol': symbol,
            'notional_brl': str(value * fx),
            'planned_risk_brl': planned_risk_brl,
        })
    return out


def build_merged_snapshot(
    ledger: dict[str, Any],
    *,
    positions_count: int,
    orders_count: int,
    broker_positions: list[dict[str, str]] | None = None,
    at_utc: datetime | None = None,
) -> dict[str, Any]:
    stamp = (at_utc or datetime.now(timezone.utc)).isoformat()
    data = dict(ledger)
    data['at_utc'] = stamp
    data['alpaca_positions_count'] = positions_count
    data['alpaca_open_orders_count'] = orders_count
    data['positions'] = broker_positions if broker_positions is not None else data.get('positions', [])
    data['has_pending_orders'] = orders_count > 0
    data['schema_version'] = 'v4-risk-snapshot-ops-1'
    return data


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    if path.suffix != '.json' or path.is_symlink():
        raise ValueError('UNSAFE_OUTPUT')
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.json.tmp')
    if temp.is_symlink():
        raise ValueError('UNSAFE_TEMP')
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temp.replace(path)


def refresh_once(
    env: dict[str, str],
    *,
    broker_get: Callable[..., Any] | None = None,
    conn_factory=None,
    now_utc: datetime | None = None,
) -> dict[str, Any]:
    getter = broker_get or get_json
    out_path = env.get('V4_RISK_SNAPSHOT_FILE', '').strip()
    if not out_path:
        _LOG.warning('risk_snapshot_refresh: V4_RISK_SNAPSHOT_FILE unset')
        return {'status': 'SKIPPED', 'reason': 'OUTPUT_PATH_MISSING', 'orders_sent': 0}
    try:
        fx = validate_env(env)
        flags = fetch_control_flags(conn_factory=conn_factory)
        planned_risk_brl = str(brl_from_cents(int(flags['max_risk_per_trade_cents'])))
        ledger = portfolio_risk_snapshot(conn_factory=conn_factory, now_utc=now_utc)
        raw_positions = getter('/v2/positions', env)
        orders = getter('/v2/orders?status=open&limit=500', env)
        if not isinstance(raw_positions, list) or not isinstance(orders, list):
            raise ValueError('INVALID_BROKER_RESPONSE')
        pos_n, ord_n = len(raw_positions), len(orders)
        broker_positions = _normalize_positions(raw_positions, fx, planned_risk_brl)
        merged = build_merged_snapshot(
            ledger,
            positions_count=pos_n,
            orders_count=ord_n,
            broker_positions=broker_positions,
            at_utc=now_utc,
        )
        _atomic_write(Path(out_path), merged)
        return {'status': 'REFRESHED', 'positions': pos_n, 'open_orders': ord_n, 'orders_sent': 0}
    except Exception as exc:
        _LOG.warning('risk_snapshot_refresh skipped: %s', type(exc).__name__)
        return {'status': 'SKIPPED', 'reason': type(exc).__name__, 'orders_sent': 0}


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(description='Refresh V4 risk snapshot (ledger + Alpaca GET)')
    parser.add_argument('--once', action='store_true', help='Single refresh then exit')
    parser.parse_args(argv)
    result = refresh_once(os.environ)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] == 'REFRESHED' else 1


if __name__ == '__main__':
    raise SystemExit(main())