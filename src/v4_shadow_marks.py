"""Deterministic, offline Shadow mark-to-market evaluator.

This module cannot certify live prices or executions. It consumes externally
provided, *complete* OHLC bars and emits hypothetical outcomes only.
Conflicting stop/target touches resolve conservatively to stop first.
"""
from datetime import datetime, timezone
from decimal import Decimal
from portfolio_risk_v4 import number


def _time(value):
    if not isinstance(value, str):
        raise ValueError('INVALID_TIME')
    value = value.replace('Z', '+00:00')
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('NAIVE_TIME')
    return parsed.astimezone(timezone.utc)


def evaluate_shadow(entry_intent, bars, *, target_brl, fee_brl='0', slippage_brl='0'):
    """Evaluate post-intent bars, never treating a paper intent as a broker fill.

    Parameters are BRL per unit except fee_brl (round-trip total BRL).
    Outcome is hypothetical, not a broker reconciliation or recommendation.
    """
    if not isinstance(entry_intent, dict) or entry_intent.get('event') != 'PAPER_ENTRY_REQUESTED_NOT_FILLED':
        raise ValueError('NOT_LOCAL_PAPER_INTENT')
    if entry_intent.get('status') != 'PENDING_VERIFIED_MARKET_FILL':
        raise ValueError('INTENT_NOT_PENDING')
    if not isinstance(bars, list):
        raise ValueError('INVALID_BARS')
    entry_time = _time(entry_intent['at_utc'])
    entry = number(entry_intent['entry_brl'])
    stop = number(entry_intent['stop_brl'])
    target = number(target_brl)
    qty = number(entry_intent['quantity'])
    fee = number(fee_brl)
    slippage = number(slippage_brl)
    if not 0 < stop < entry < target or qty <= 0 or fee < 0 or slippage < 0:
        raise ValueError('INVALID_TRADE_PARAMETERS')
    previous = entry_time
    last_close = None
    last_time = None
    for bar in bars:
        if not isinstance(bar, dict) or bar.get('complete') is not True or bar.get('verified') is not True:
            raise ValueError('UNVERIFIED_OR_INCOMPLETE_BAR')
        timestamp = _time(bar['at_utc'])
        if timestamp <= previous:
            raise ValueError('BAR_NOT_STRICTLY_AFTER_INTENT_OR_PREVIOUS_BAR')
        previous = timestamp
        op, hi, lo, close = (number(bar[field]) for field in ('open_brl', 'high_brl', 'low_brl', 'close_brl'))
        if not 0 < lo <= op <= hi or not lo <= close <= hi:
            raise ValueError('INVALID_OHLC')
        # Conservative stop-first when both boundaries are touched in one bar.
        # Gap through stop is modeled at opening price (worse than stop).
        if lo <= stop:
            exit_price = min(op, stop) - slippage
            return _result('HYPOTHETICAL_STOP', entry_intent, timestamp, entry, exit_price, qty, fee)
        if hi >= target:
            # Do not claim a better fill on a gap above the target.
            exit_price = target - slippage
            return _result('HYPOTHETICAL_TARGET', entry_intent, timestamp, entry, exit_price, qty, fee)
        last_close, last_time = close, timestamp
    if last_close is None:
        return {'status': 'HYPOTHETICAL_PENDING', 'signal_id': entry_intent.get('signal_id'), 'broker_filled': False}
    gross = qty * (last_close - entry)
    return {'status': 'HYPOTHETICAL_OPEN', 'signal_id': entry_intent.get('signal_id'),
            'mark_time_utc': last_time.isoformat(), 'unrealized_pnl_brl': str(gross - fee),
            'broker_filled': False, 'source': 'OFFLINE_SHADOW_OHLC'}


def _result(status, intent, timestamp, entry, exit_price, qty, fee):
    return {'status': status, 'signal_id': intent.get('signal_id'),
            'at_utc': timestamp.isoformat(), 'hypothetical_exit_brl': str(exit_price),
            'hypothetical_net_pnl_brl': str(qty * (exit_price-entry) - fee),
            'broker_filled': False, 'source': 'OFFLINE_SHADOW_OHLC'}
