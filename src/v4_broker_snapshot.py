"""Read-only partial cross-market risk snapshot from Alpaca Paper.

Intentionally NEVER attests cross-market completeness or P&L. This artifact must
not authorize orders until independent B3/crypto positions and verified P&L are
reconciled. Fetches account, positions and open orders using allowlisted GETs.
"""
import argparse
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

try:
    from .paper_audit import validate_env, get_json, amount
except ImportError:
    from paper_audit import validate_env, get_json, amount


def build_snapshot(account, positions, orders, fx, *, at=None):
    if not isinstance(account, dict) or not isinstance(positions, list) or not isinstance(orders, list):
        raise ValueError('INVALID_BROKER_RESPONSE')
    if account.get('status') != 'ACTIVE' or account.get('currency') != 'USD' or account.get('trading_blocked') is not False:
        raise ValueError('BROKER_ACCOUNT_NOT_READY')
    if amount(fx) <= 0:
        raise ValueError('INVALID_FX')
    cash = amount(account['cash'])
    if cash < 0:
        raise ValueError('NEGATIVE_CASH')
    normalized = []
    seen = set()
    for p in positions:
        if not isinstance(p, dict) or not isinstance(p.get('symbol'), str) or not p['symbol'].strip():
            raise ValueError('INVALID_POSITION')
        if p.get('side') != 'long':
            raise ValueError('SHORT_POSITION')
        symbol = p['symbol'].strip().upper()
        if symbol in seen:
            raise ValueError('DUPLICATE_POSITION')
        seen.add(symbol)
        value = amount(p['market_value'])
        if value <= 0:
            raise ValueError('INVALID_MARKET_VALUE')
        asset_class = p.get('asset_class')
        market = {'us_equity': 'US_EQUITY', 'crypto': 'CRYPTO'}.get(asset_class)
        if market is None:
            raise ValueError('UNKNOWN_ASSET_CLASS')
        normalized.append({'market': market, 'symbol': symbol,
                           'notional_brl': str(value * fx),
                           # Stop risk cannot be inferred from broker market value.
                           'planned_risk_brl': None})
    for order in orders:
        if not isinstance(order, dict) or not isinstance(order.get('id'), str):
            raise ValueError('INVALID_PENDING_ORDER')
    return {
        'schema_version': 'v4-broker-snapshot-1',
        'source': 'ALPACA_PAPER_GET_ONLY',
        'at_utc': (at or datetime.now(timezone.utc)).isoformat(),
        'reference_fx_brl_per_usd': str(fx),
        'cash_alpaca_brl_reference': str(cash * fx),
        'broker_positions': normalized,
        'broker_open_order_count': len(orders),
        # Never forge completeness from a single broker or from approximate FX.
        'complete': False,
        'daily_pnl_verified': False,
        'weekly_pnl_verified': False,
        'broker_reconciled': False,
        'positions': normalized,
        'daily_pnl_brl': None,
        'weekly_pnl_brl': None,
        'available_cash_brl': None,
        'has_pending_orders': True if orders else None,
        'execution_authorized': False,
        'orders_sent': 0,
        'blocking_reasons': ['CROSS_MARKET_COVERAGE_MISSING', 'VERIFIED_PNL_MISSING',
                             'POSITION_STOP_RISK_MISSING', 'FX_REFERENCE_NOT_LIVE',
                             'ALPACA_OPEN_ORDERS_NOT_ATTESTED_ACROSS_MARKETS'],
    }


def collect(env, *, getter=get_json):
    fx = validate_env(env)
    account = getter('/v2/account', env)
    positions = getter('/v2/positions', env)
    orders = getter('/v2/orders?status=open&limit=500', env)
    return build_snapshot(account, positions, orders, fx)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only partial Alpaca Paper snapshot; never permits orders')
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        output = Path(args.output)
        if output.suffix != '.json' or output.is_symlink():
            raise ValueError('UNSAFE_OUTPUT')
        data = collect(os.environ)
        output.parent.mkdir(parents=True, exist_ok=True)
        temp = output.with_suffix('.json.tmp')
        if temp.is_symlink():
            raise ValueError('UNSAFE_TEMP')
        temp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        temp.replace(output)
        print(json.dumps({'status': 'PARTIAL_READ_ONLY', 'positions': len(data['positions']), 'orders_sent': 0}))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
