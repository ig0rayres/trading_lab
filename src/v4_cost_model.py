"""Conservative economic cost model for Paper/Shadow results.

Amounts in the same currency as the trade. Monetary costs are nonnegative;
price-impact basis points are charged per side, not on the round trip total.
All assumptions must be explicitly supplied. No source data is fabricated.
"""
from decimal import Decimal, InvalidOperation


def dec(value, name, allow_zero=True):
    if isinstance(value, bool):
        raise ValueError('INVALID_' + name)
    try:
        v = Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        raise ValueError('INVALID_' + name)
    if not v.is_finite() or v < 0 or (not allow_zero and v == 0):
        raise ValueError('INVALID_' + name)
    return v


def economic_result(payload):
    """Estimate net result for a fully closed long trade.

    Explicit estimates for spread/slippage represent *incremental* costs, not
    spreads already embedded in observed executable fill prices. Callers must
    set those fields to zero when fills already capture the corresponding cost.
    Fixed monthly overhead is allocated by an explicit trades/month estimate,
    not silently deducted from every trade in full.
    """
    if not isinstance(payload, dict):
        raise ValueError('INVALID_PAYLOAD')
    currency = payload.get('currency')
    if currency not in ('BRL', 'USD'):
        raise ValueError('UNSUPPORTED_CURRENCY')
    qty = dec(payload.get('quantity'), 'QUANTITY', False)
    entry = dec(payload.get('entry_price'), 'ENTRY', False)
    exit_price = dec(payload.get('exit_price'), 'EXIT', False)
    costs = payload.get('costs')
    if not isinstance(costs, dict):
        raise ValueError('UNKNOWN_COSTS')
    required = ('entry_commission', 'exit_commission', 'exchange_fees', 'taxes',
                'spread_bps_entry', 'spread_bps_exit', 'slippage_bps_entry',
                'slippage_bps_exit', 'funding', 'fx_fees', 'monthly_subscriptions',
                'monthly_data', 'monthly_infra', 'expected_monthly_trades')
    for name in required:
        if name not in costs:
            raise ValueError('MISSING_COST_' + name.upper())
    values = {k: dec(costs[k], k.upper(), k != 'expected_monthly_trades') for k in required}
    if costs.get('impact_already_in_fill') is not False and (
        values['spread_bps_entry'] or values['spread_bps_exit'] or
        values['slippage_bps_entry'] or values['slippage_bps_exit']
    ):
        raise ValueError('AMBIGUOUS_IMPACT_DOUBLE_COUNT')
    entry_notional = entry * qty
    exit_notional = exit_price * qty
    entry_bps = values['spread_bps_entry'] + values['slippage_bps_entry']
    exit_bps = values['spread_bps_exit'] + values['slippage_bps_exit']
    impact = (entry_notional * entry_bps + exit_notional * exit_bps) / Decimal('10000')
    overhead = (values['monthly_subscriptions'] + values['monthly_data'] +
                values['monthly_infra']) / values['expected_monthly_trades']
    variable = sum((values[k] for k in ('entry_commission','exit_commission','exchange_fees',
                                        'taxes','funding','fx_fees')), Decimal('0')) + impact
    gross = exit_notional - entry_notional
    net = gross - variable - overhead
    return {'schema_version': 'v4-economic-costs-1', 'mode': 'RESEARCH',
            'currency': currency, 'gross_pnl': str(gross),
            'variable_costs': str(variable), 'allocated_overhead': str(overhead),
            'total_costs': str(variable + overhead), 'economic_net_pnl': str(net),
            'net_positive': net > 0, 'assumptions_supplied': True,
            'broker_verified': False, 'orders_sent': 0}
