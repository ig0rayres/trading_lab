"""Read-only Alpaca PAPER account audit. No order mutation imports or methods."""
import argparse
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.request import Request, urlopen

PAPER_URL = 'https://paper-api.alpaca.markets'


def amount(x):
    try:
        d = Decimal(str(x))
        if not d.is_finite():
            raise ValueError('nonfinite')
        return d
    except (InvalidOperation, ValueError) as exc:
        raise ValueError('Invalid numeric value') from exc


def validate_env(env):
    if env.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        raise ValueError('LIVE_TRADING_ENABLED must be false')
    if env.get('ALPACA_PAPER_TRADE', '').lower() != 'true':
        raise ValueError('ALPACA_PAPER_TRADE must be true')
    if env.get('ALPACA_BASE_URL', '').rstrip('/') != PAPER_URL:
        raise ValueError('Paper endpoint mismatch')
    if not env.get('ALPACA_API_KEY') or not env.get('ALPACA_SECRET_KEY'):
        raise ValueError('Paper credentials missing')
    if not env.get('USD_BRL_REFERENCE'):
        raise ValueError('USD_BRL_REFERENCE required: explicit BRL per USD, not fetched or guessed')
    fx = amount(env['USD_BRL_REFERENCE'])
    if not Decimal('2') <= fx <= Decimal('12'):
        raise ValueError('USD_BRL_REFERENCE outside sanity range')
    return fx


def get_json(endpoint, env, opener=urlopen):
    if endpoint not in ('/v2/account', '/v2/positions', '/v2/orders?status=open&limit=500'):
        raise ValueError('GET endpoint not allowlisted')
    req = Request(PAPER_URL + endpoint, headers={
        'APCA-API-KEY-ID': env['ALPACA_API_KEY'],
        'APCA-API-SECRET-KEY': env['ALPACA_SECRET_KEY'],
    }, method='GET')
    with opener(req, timeout=15) as response:
        return json.load(response)


def audit(account, positions, orders, fx):
    cap_brl = Decimal('5000')
    cap_usd = cap_brl / fx
    risk_usd = Decimal('50') / fx
    equity = amount(account.get('equity', '0'))
    cash = amount(account.get('cash', '0'))
    if not isinstance(positions, list) or not isinstance(orders, list):
        raise ValueError('Unexpected Alpaca positions/orders response')
    long_exposure = Decimal('0')
    short_symbols = []
    for p in positions:
        side = str(p.get('side', '')).lower()
        val = amount(p.get('market_value', '0'))
        if side != 'long' or val < 0:
            short_symbols.append(p.get('symbol', 'UNKNOWN'))
        else:
            long_exposure += val
    flags = []
    if account.get('status') != 'ACTIVE': flags.append('ACCOUNT_NOT_ACTIVE')
    if account.get('currency') != 'USD': flags.append('CURRENCY_NOT_USD')
    if account.get('trading_blocked'): flags.append('BROKER_TRADING_BLOCKED')
    if len(positions) > 3: flags.append('OVER_THREE_POSITIONS')
    if short_symbols: flags.append('SHORT_POSITION_FOUND')
    if long_exposure > cap_usd: flags.append('CAPITAL_LIMIT_EXCEEDED')
    if orders: flags.append('OPEN_ORDERS_REQUIRE_REVIEW')
    if equity <= 0 or cash < 0: flags.append('ACCOUNT_EQUITY_OR_CASH_INVALID')
    # A read-only snapshot cannot prove 1% stop risk or absence of leverage.
    flags.extend(['ORDER_RISK_NOT_VERIFIED', 'LEVERAGE_POLICY_NOT_ENFORCED'])
    return {
        'status': 'READ_ONLY_DIAGNOSTIC_NO_ORDERS',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'broker': 'alpaca', 'endpoint': PAPER_URL,
        'reference_fx_brl_per_usd': str(fx),
        'capital_ceiling_brl': str(cap_brl),
        'capital_ceiling_usd': str(cap_usd.quantize(Decimal('0.01'))),
        'planned_risk_per_trade_brl': '50.00',
        'planned_risk_per_trade_usd': str(risk_usd.quantize(Decimal('0.01'))),
        'max_positions': 3, 'account_status': account.get('status'),
        'account_currency': account.get('currency'),
        'account_equity_usd': str(equity), 'account_cash_usd': str(cash),
        'open_positions': len(positions), 'long_market_exposure_usd': str(long_exposure),
        'open_orders': len(orders), 'short_symbols': short_symbols,
        'flags': flags, 'paper_execution_authorized': False,
        'live_execution_authorized': False,
        'notes': ['Read-only snapshot; cannot enforce limits on future orders.',
                  'Swing-trade gaps may exceed planned stop loss.',
                  'FX is a user-supplied reference rate, not a live quote.']
    }


def main():
    parser = argparse.ArgumentParser(description='Alpaca paper read-only diagnostic')
    parser.add_argument('--output', default='/app/reports/paper/paper-audit.json')
    args = parser.parse_args()
    env = os.environ
    try:
        fx = validate_env(env)
        result = audit(get_json('/v2/account', env), get_json('/v2/positions', env),
                       get_json('/v2/orders?status=open&limit=500', env), fx)
    except Exception as exc:
        # Avoid echoing secrets or request headers in exceptions.
        raise SystemExit('Paper read-only audit failed: ' + type(exc).__name__ + '. Verify environment, API access and FX reference.')
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
