"""Refresh V4 risk snapshot file with fresh Alpaca paper GET counts and at_utc.

Read-only broker access (paper_audit allowlisted GETs). Never places orders.
Merges ledger-verified P&L from portfolio_risk_snapshot when LEDGER_DATABASE_URL is set.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from paper_audit import amount, get_json, validate_env
from risk_control_flags import brl_from_cents, fetch_control_flags

SCHEMA_VERSION = 'risk-snapshot-refresh-1'
_ASSET_TO_MARKET = {'us_equity': 'US_EQUITY', 'crypto': 'CRYPTO'}


def _planned_risk_for_symbol(
    symbol: str,
    *,
    prior_positions: list[dict[str, Any]] | None,
    conservative_brl: str,
) -> str:
    sym = symbol.strip().upper()
    if prior_positions:
        for row in prior_positions:
            if not isinstance(row, dict):
                continue
            if str(row.get('symbol', '')).strip().upper() == sym:
                risk = row.get('planned_risk_brl')
                if risk is not None and str(risk).strip():
                    return str(risk)
    return conservative_brl


def _alpaca_positions_snapshot(
    positions: list[dict[str, Any]],
    fx,
    *,
    prior_positions: list[dict[str, Any]] | None,
    conservative_risk_brl: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for raw in positions:
        if not isinstance(raw, dict):
            continue
        if raw.get('side') != 'long':
            continue
        market = _ASSET_TO_MARKET.get(str(raw.get('asset_class', '')).lower())
        symbol = str(raw.get('symbol', '')).strip().upper()
        if not market or not symbol:
            continue
        value = amount(raw.get('market_value', '0'))
        if value <= 0:
            continue
        notional_brl = value * fx
        out.append(
            {
                'market': market,
                'symbol': symbol,
                'notional_brl': str(notional_brl),
                'planned_risk_brl': _planned_risk_for_symbol(
                    symbol,
                    prior_positions=prior_positions,
                    conservative_brl=conservative_risk_brl,
                ),
            }
        )
    return out


def build_refresh_snapshot(
    env: dict[str, str],
    *,
    getter: Callable[..., Any] = get_json,
    conn_factory: Callable[..., Any] | None = None,
    now: datetime | None = None,
    prior: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Collect broker counts and merge with ledger portfolio snapshot fields."""
    fx = validate_env(env)
    account = getter('/v2/account', env)
    positions_raw = getter('/v2/positions', env)
    orders_raw = getter('/v2/orders?status=open&limit=500', env)
    if not isinstance(positions_raw, list) or not isinstance(orders_raw, list):
        raise ValueError('INVALID_BROKER_RESPONSE')

    from ledger_loss_anchor import portfolio_risk_snapshot

    ledger_snap = portfolio_risk_snapshot(conn_factory=conn_factory)
    flags = fetch_control_flags(conn_factory=conn_factory)
    conservative_risk = str(brl_from_cents(int(flags['max_risk_per_trade_cents'])))
    prior_positions = (prior or {}).get('positions')
    if not isinstance(prior_positions, list):
        prior_positions = ledger_snap.get('positions') if isinstance(ledger_snap.get('positions'), list) else []

    mapped_positions = _alpaca_positions_snapshot(
        positions_raw,
        fx,
        prior_positions=prior_positions,
        conservative_risk_brl=conservative_risk,
    )
    cash_usd = amount(account.get('cash', '0'))
    available_cash = str(cash_usd * fx) if cash_usd >= 0 else ledger_snap.get('available_cash_brl', '0')

    at = (now or datetime.now(timezone.utc)).isoformat()
    return {
        'schema_version': SCHEMA_VERSION,
        'source': 'RISK_SNAPSHOT_REFRESH_ALPACA_PAPER_GET',
        'at_utc': at,
        'alpaca_positions_count': len(positions_raw),
        'alpaca_open_orders_count': len(orders_raw),
        'reference_fx_brl_per_usd': str(fx),
        'complete': ledger_snap.get('complete'),
        'daily_pnl_verified': ledger_snap.get('daily_pnl_verified'),
        'weekly_pnl_verified': ledger_snap.get('weekly_pnl_verified'),
        'broker_reconciled': ledger_snap.get('broker_reconciled'),
        'positions': mapped_positions,
        'daily_pnl_brl': ledger_snap.get('daily_pnl_brl', '0'),
        'weekly_pnl_brl': ledger_snap.get('weekly_pnl_brl', '0'),
        'available_cash_brl': available_cash,
        'has_pending_orders': bool(orders_raw),
        'orders_sent': 0,
    }


def _load_prior(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def write_snapshot_atomic(path: Path, data: dict[str, Any]) -> None:
    if path.suffix != '.json' or path.is_symlink():
        raise ValueError('UNSAFE_OUTPUT_PATH')
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.json.tmp')
    if temp.is_symlink():
        raise ValueError('UNSAFE_TEMP_PATH')
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temp.replace(path)


def refresh_to_file(
    env: dict[str, str],
    output: str | Path,
    *,
    getter: Callable[..., Any] = get_json,
    conn_factory: Callable[..., Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    out_path = Path(output)
    prior = _load_prior(out_path) if out_path.exists() else None
    data = build_refresh_snapshot(
        env,
        getter=getter,
        conn_factory=conn_factory,
        now=now,
        prior=prior,
    )
    write_snapshot_atomic(out_path, data)
    return data


def maybe_auto_refresh_risk_snapshot(
    env: dict[str, str],
    *,
    getter: Callable[..., Any] = get_json,
) -> bool:
    """When RISK_SNAPSHOT_AUTO_REFRESH=true, refresh V4_RISK_SNAPSHOT_FILE before submit."""
    if env.get('RISK_SNAPSHOT_AUTO_REFRESH', 'false').lower() != 'true':
        return False
    target = (env.get('V4_RISK_SNAPSHOT_FILE') or '').strip()
    if not target:
        return False
    try:
        refresh_to_file(env, target, getter=getter)
        return True
    except Exception:
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Refresh risk-snapshot.json from Alpaca paper GETs (read-only)',
    )
    parser.add_argument(
        '--output',
        default=os.environ.get('V4_RISK_SNAPSHOT_FILE', '/app/data/risk-snapshot.json'),
        help='Snapshot JSON path (default: V4_RISK_SNAPSHOT_FILE or /app/data/risk-snapshot.json)',
    )
    args = parser.parse_args(argv)
    try:
        data = refresh_to_file(os.environ, args.output)
        print(
            json.dumps(
                {
                    'status': 'REFRESHED',
                    'at_utc': data['at_utc'],
                    'alpaca_positions_count': data['alpaca_positions_count'],
                    'alpaca_open_orders_count': data['alpaca_open_orders_count'],
                    'orders_sent': 0,
                },
                ensure_ascii=False,
            )
        )
        return 0
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())