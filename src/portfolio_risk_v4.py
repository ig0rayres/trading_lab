"""Pure, fail-closed portfolio risk evaluator across US, B3 and crypto.

No market data access and no broker actions. It cannot certify broker state.
All money is denominated in BRL; risk is planned, not guaranteed gap loss.
"""
from decimal import Decimal, InvalidOperation
from typing import Any, Callable

from risk_control_flags import TIGHT_DEFAULTS, brl_from_cents, fetch_control_flags
from demo_account_gate import NO_DEMO_ACCOUNT_PATH, demo_market_block_reason

ALLOWED_MARKETS = frozenset(('US_EQUITY', 'B3_EQUITY', 'CRYPTO', 'FOREX'))


def _limits_from_flags(flags: dict[str, Any]) -> dict[str, Decimal | int]:
    return {
        'capital': brl_from_cents(int(flags['capital_cents'])),
        'max_trade': brl_from_cents(int(flags['max_risk_per_trade_cents'])),
        'default_trade': brl_from_cents(int(flags['max_risk_per_trade_cents'])),
        'prodigy_trade': brl_from_cents(int(flags['prodigy_risk_cents'])),
        'max_aggregate': brl_from_cents(int(flags['max_aggregate_risk_cents'])),
        'max_daily_loss': brl_from_cents(int(flags['max_daily_loss_cents'])),
        'max_weekly_loss': brl_from_cents(int(flags['max_weekly_loss_cents'])),
        'max_positions': int(flags['max_open_positions']),
    }


def resolve_limits(*, conn_factory: Callable[..., Any] | None = None) -> dict[str, Decimal | int]:
    return _limits_from_flags(fetch_control_flags(conn_factory=conn_factory))


def number(value):
    if isinstance(value, bool):
        raise ValueError('boolean monetary input')
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError('invalid monetary input') from exc
    if not result.is_finite():
        raise ValueError('nonfinite monetary input')
    return result


def evaluate(
    candidate,
    snapshot,
    *,
    conn_factory: Callable[..., Any] | None = None,
    limits: dict[str, Decimal | int] | None = None,
):
    """Return allow=False for missing verification, even in simulation."""
    lim = limits or resolve_limits(conn_factory=conn_factory)
    capital = lim['capital']
    max_trade = lim['max_trade']
    default_trade = lim['default_trade']
    prodigy_trade = lim['prodigy_trade']
    max_aggregate = lim['max_aggregate']
    max_daily_loss = lim['max_daily_loss']
    max_weekly_loss = lim['max_weekly_loss']
    max_positions = int(lim['max_positions'])
    reasons = []
    try:
        if candidate['market'] not in ALLOWED_MARKETS:
            reasons.append('UNSUPPORTED_MARKET')
        if candidate.get('market') == 'FOREX':
            demo_block = demo_market_block_reason('FOREX')
            if demo_block:
                reasons.append(demo_block)
        if not isinstance(candidate.get('symbol'), str) or not candidate['symbol'].strip():
            reasons.append('INVALID_SYMBOL')
        if candidate.get('side') != 'buy':
            reasons.append('LONG_ONLY')
        if candidate.get('verified') is not True:
            reasons.append('UNVERIFIED_SIGNAL')
        if candidate.get('trading_mode') != 'PAPER':
            reasons.append('NOT_PAPER')
        if snapshot.get('complete') is not True:
            reasons.append('INCOMPLETE_CROSS_MARKET_SNAPSHOT')
        if snapshot.get('daily_pnl_verified') is not True or snapshot.get('weekly_pnl_verified') is not True:
            reasons.append('LOSS_DATA_NOT_VERIFIED')
        if snapshot.get('broker_reconciled') is not True:
            reasons.append('BROKER_NOT_RECONCILED')
        qty = number(candidate['quantity'])
        entry, stop = number(candidate['entry_brl']), number(candidate['stop_brl'])
        if qty <= 0 or (candidate['market'] != 'CRYPTO' and qty != qty.to_integral_value()) or stop <= 0 or entry <= stop:
            reasons.append('INVALID_ENTRY_STOP_OR_QUANTITY')
        positions = snapshot['positions']
        if not isinstance(positions, list):
            reasons.append('INVALID_POSITIONS')
            positions = []
        if len(positions) >= max_positions:
            reasons.append('MAX_POSITIONS')
        for p in positions:
            if not isinstance(p, dict) or p.get('market') not in ALLOWED_MARKETS or not isinstance(p.get('symbol'), str) or not p['symbol'].strip():
                reasons.append('INVALID_EXISTING_POSITION')
                raise ValueError('bad portfolio position')
        identities = [(p['market'], p['symbol'].strip().upper()) for p in positions]
        if len(set(identities)) != len(identities):
            reasons.append('DUPLICATE_EXISTING_POSITIONS')
        if (candidate['market'], candidate['symbol'].strip().upper()) in identities:
            reasons.append('DUPLICATE_EXPOSURE')
        exposed = sum((number(p['notional_brl']) for p in positions), Decimal(0))
        at_risk = sum((number(p['planned_risk_brl']) for p in positions), Decimal(0))
        if any(number(p['notional_brl']) <= 0 or number(p['planned_risk_brl']) <= 0 for p in positions):
            reasons.append('INVALID_EXISTING_POSITION')
        planned_risk = qty * (entry - stop)
        notional = qty * entry
        if planned_risk <= 0 or planned_risk > max_trade:
            reasons.append('MAX_TRADE_RISK')
        risk_tier = prodigy_trade if candidate.get('prodigy') is True else default_trade
        if planned_risk > risk_tier:
            reasons.append('DEFAULT_TRADE_RISK')
        if at_risk + planned_risk > max_aggregate:
            reasons.append('AGGREGATE_RISK_LIMIT')
        if exposed + notional > capital:
            reasons.append('CAPITAL_LIMIT')
        daily_pnl = number(snapshot['daily_pnl_brl'])
        weekly_pnl = number(snapshot['weekly_pnl_brl'])
        if daily_pnl <= -max_daily_loss or daily_pnl - planned_risk < -max_daily_loss:
            reasons.append('DAILY_LOSS_HALT')
        if weekly_pnl <= -max_weekly_loss or weekly_pnl - planned_risk < -max_weekly_loss:
            reasons.append('WEEKLY_LOSS_HALT')
        if number(snapshot['available_cash_brl']) < 0:
            reasons.append('INVALID_CASH')
        if number(snapshot['available_cash_brl']) < notional:
            reasons.append('INSUFFICIENT_CASH')
        if snapshot.get('has_pending_orders') is not False:
            reasons.append('PENDING_ORDERS_UNVERIFIED')
    except (KeyError, ValueError, TypeError, AttributeError):
        reasons.append('MISSING_OR_INVALID_RISK_INPUT')
    uniq = sorted(set(reasons))
    reject_code = NO_DEMO_ACCOUNT_PATH if NO_DEMO_ACCOUNT_PATH in uniq else None
    return {
        'allowed': not reasons,
        'reasons': uniq,
        'reject_code': reject_code,
        'mode': 'PURE_VALIDATION_NO_ORDERS',
        'orders_sent': 0,
    }
