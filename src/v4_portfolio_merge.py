"""Conservative, read-only merger of US/B3/crypto Paper observations.

The merger is NOT a portfolio attestation. Paper intents are not fills and
Alpaca account cash isn't automatically fungible with other markets.
"""
import argparse
import json
import os
from decimal import Decimal
from pathlib import Path

try:
    from .portfolio_risk_v4 import ALLOWED_MARKETS, number
except ImportError:
    from portfolio_risk_v4 import ALLOWED_MARKETS, number


def merge(alpaca, b3, crypto):
    if not isinstance(alpaca, dict) or alpaca.get('source') != 'ALPACA_PAPER_GET_ONLY' or alpaca.get('complete') is not False:
        raise ValueError('INVALID_ALPACA_PARTIAL')
    if not isinstance(b3, dict) or not isinstance(crypto, dict):
        raise ValueError('INVALID_MARKET_OBSERVATIONS')
    combined = []
    seen = set()
    issues = []
    for source, obj, markets in (
        ('ALPACA', alpaca, {'US_EQUITY', 'CRYPTO'}),
        ('B3_SHADOW', b3, {'B3_EQUITY'}),
        ('CRYPTO_SHADOW', crypto, {'CRYPTO'}),
    ):
        records = obj.get('positions')
        if not isinstance(records, list):
            raise ValueError('INVALID_POSITIONS_' + source)
        if source != 'ALPACA' and obj.get('mode') != 'SHADOW':
            raise ValueError('INVALID_SHADOW_SOURCE')
        for p in records:
            if not isinstance(p, dict) or p.get('market') not in markets or not isinstance(p.get('symbol'), str) or not p['symbol'].strip():
                raise ValueError('INVALID_POSITION_' + source)
            symbol = p['symbol'].strip().upper()
            key = (p['market'], symbol)
            if key in seen:
                raise ValueError('DUPLICATE_CROSS_SOURCE_POSITION')
            seen.add(key)
            notional = number(p['notional_brl'])
            if notional <= 0:
                raise ValueError('INVALID_NOTIONAL')
            risk = p.get('planned_risk_brl')
            if risk is None:
                issues.append('STOP_RISK_UNKNOWN:' + source + ':' + symbol)
            elif number(risk) <= 0:
                raise ValueError('INVALID_PLANNED_RISK')
            combined.append({'source': source, 'market': p['market'], 'symbol': symbol,
                             'notional_brl': str(notional), 'planned_risk_brl': str(number(risk)) if risk is not None else None})
    # Shadow data cannot attest custody, fills, realized P&L or cash. Never
    # trust user-provided flags to promote this observational report to safe.
    return {'schema_version': 'v4-cross-market-observation-1', 'mode': 'READ_ONLY',
            'positions': combined, 'complete': False, 'broker_reconciled': False,
            'daily_pnl_verified': False, 'weekly_pnl_verified': False,
            'daily_pnl_brl': None, 'weekly_pnl_brl': None,
            'available_cash_brl': None, 'has_pending_orders': True,
            'execution_authorized': False, 'automatic_order_submission': False,
            'orders_sent': 0, 'issues': sorted(set(issues + [
                'B3_CRYPTO_SHADOW_NOT_BROKER_ATTESTED', 'CROSS_MARKET_CASH_UNVERIFIED',
                'CROSS_MARKET_PNL_UNVERIFIED', 'CROSS_MARKET_PENDING_ORDERS_UNVERIFIED']))}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Merge Paper observations; always blocks execution')
    parser.add_argument('--alpaca', required=True)
    parser.add_argument('--b3', required=True)
    parser.add_argument('--crypto', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        print(json.dumps({'status': 'BLOCKED_LIVE_FLAG', 'orders_sent': 0})); return 2
    try:
        source = lambda path: json.loads(Path(path).read_text(encoding='utf-8'))
        report = merge(source(args.alpaca), source(args.b3), source(args.crypto))
        output = Path(args.output)
        if output.suffix != '.json' or output.is_symlink():
            raise ValueError('UNSAFE_OUTPUT')
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix('.json.tmp')
        if temporary.is_symlink():
            raise ValueError('UNSAFE_TEMP')
        temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        temporary.replace(output)
        print(json.dumps({'status': 'PARTIAL_READ_ONLY', 'positions': len(report['positions']), 'orders_sent': 0}))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
