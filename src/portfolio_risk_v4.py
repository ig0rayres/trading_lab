"""Pure, fail-closed portfolio risk evaluator across US, B3 and crypto.

No market data access and no broker actions. It cannot certify broker state.
All money is denominated in BRL; risk is planned, not guaranteed gap loss.
"""
from decimal import Decimal, InvalidOperation

CAPITAL = Decimal('10000')
MAX_TRADE = Decimal('100')
DEFAULT_TRADE = Decimal('50')
PRODIGY_TRADE = Decimal('20')
MAX_AGGREGATE = Decimal('200')
MAX_DAILY_LOSS = Decimal('200')
MAX_WEEKLY_LOSS = Decimal('500')
MAX_POSITIONS = 3
ALLOWED_MARKETS = frozenset(('US_EQUITY', 'B3_EQUITY', 'CRYPTO'))


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


def evaluate(candidate, snapshot):
    """Return allow=False for missing verification, even in simulation."""
    reasons = []
    try:
        if candidate['market'] not in ALLOWED_MARKETS:
            reasons.append('UNSUPPORTED_MARKET')
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
        if len(positions) >= MAX_POSITIONS:
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
        planned_risk = qty * (entry-stop)
        notional = qty * entry
        if planned_risk <= 0 or planned_risk > MAX_TRADE:
            reasons.append('MAX_TRADE_RISK')
        risk_tier = PRODIGY_TRADE if candidate.get('prodigy') is True else DEFAULT_TRADE
        # Strategy signals cannot self-authorize higher risk with an arbitrary boolean.
        if planned_risk > risk_tier:
            reasons.append('DEFAULT_TRADE_RISK')
        if at_risk + planned_risk > MAX_AGGREGATE:
            reasons.append('AGGREGATE_RISK_LIMIT')
        if exposed + notional > CAPITAL:
            reasons.append('CAPITAL_LIMIT')
        daily_pnl = number(snapshot['daily_pnl_brl'])
        weekly_pnl = number(snapshot['weekly_pnl_brl'])
        # Do not open a position whose planned stop would exceed the loss budget.
        # Gap/slippage can cause larger losses; this is only the pre-trade bound.
        if daily_pnl <= -MAX_DAILY_LOSS or daily_pnl - planned_risk < -MAX_DAILY_LOSS:
            reasons.append('DAILY_LOSS_HALT')
        if weekly_pnl <= -MAX_WEEKLY_LOSS or weekly_pnl - planned_risk < -MAX_WEEKLY_LOSS:
            reasons.append('WEEKLY_LOSS_HALT')
        if number(snapshot['available_cash_brl']) < 0:
            reasons.append('INVALID_CASH')
        if number(snapshot['available_cash_brl']) < notional:
            reasons.append('INSUFFICIENT_CASH')
        if snapshot.get('has_pending_orders') is not False:
            reasons.append('PENDING_ORDERS_UNVERIFIED')
    except (KeyError, ValueError, TypeError, AttributeError):
        reasons.append('MISSING_OR_INVALID_RISK_INPUT')
    return {'allowed': not reasons, 'reasons': sorted(set(reasons)),
            'mode': 'PURE_VALIDATION_NO_ORDERS', 'orders_sent': 0}
