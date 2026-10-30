"""Gate B: upstream trader-risk check + Trading Lab paper policy. No broker calls."""
from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

from paper_audit import amount

PAPER_CAPITAL_BRL = Decimal('5000')
PAPER_RISK_BRL = Decimal('50')
PAPER_DAILY_LOSS_BRL = Decimal('200')
MAX_CONCURRENT_TRADES = 3


def kill_switch_active(env: dict[str, str] | None = None, conn_factory=None) -> bool:
    env = env or os.environ
    if env.get('TRADING_LAB_KILL_SWITCH', '').lower() in ('1', 'true', 'yes', 'on'):
        return True
    if not os.environ.get('LEDGER_DATABASE_URL', '').strip():
        return False
    if conn_factory is None:
        from ledger_store import connect

        conn_factory = connect
    try:
        with conn_factory() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT kill_switch_on FROM control_flags WHERE deleted_at IS NULL '
                    'ORDER BY created_at DESC LIMIT 1'
                )
                row = cur.fetchone()
        return bool(row and row[0])
    except Exception:
        return False


def config_for_fx(fx: Decimal) -> dict[str, Any]:
    cap_usd = float(PAPER_CAPITAL_BRL / fx)
    return {
        'budget': cap_usd,
        'max_loss_per_trade_usd': float(PAPER_RISK_BRL / fx),
        'max_daily_loss_usd': float(PAPER_DAILY_LOSS_BRL / fx),
        'max_trades_per_day': MAX_CONCURRENT_TRADES,
        'max_orders_per_day': MAX_CONCURRENT_TRADES,
        'max_order_usd': cap_usd,
        'paper': True,
        'require_stop': True,
        'min_reward_risk': 2.0,
        'allow_short': False,
        'allow_margin': False,
    }


def signal_to_bracket_order(signal: dict[str, Any]) -> dict[str, Any]:
    entry = float(amount(signal['entry']))
    stop = float(amount(signal['stop']))
    target = float(amount(signal['target']))
    qty = int(signal['quantity'])
    sym = str(signal['symbol']).upper()
    return {
        'symbol': sym,
        'side': 'buy',
        'qty': str(qty),
        'type': 'limit',
        'time_in_force': 'day',
        'limit_price': '%.2f' % entry,
        'order_class': 'bracket',
        'take_profit_limit_price': '%.2f' % target,
        'stop_loss_stop_price': '%.2f' % stop,
        'plan': {'entry': entry, 'stop': stop, 'target': target},
    }


def evaluate_signed_signal(
    signal: dict[str, Any],
    *,
    fx: Decimal,
    portfolio=None,
    state=None,
    now=None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Return decision dict: paper_allowed | rejected with reject_code."""
    if kill_switch_active(env):
        return {'decision': 'rejected', 'reject_code': 'KILL_SWITCH', 'risk_amount_cents': 0}
    from original import load_original

    risk = load_original().risk
    order = signal_to_bracket_order(signal)
    prices = {order['symbol']: order['plan']['entry']}
    price_times = {order['symbol']: now} if now is not None else None
    res = risk.check(
        [order],
        config_for_fx(fx),
        portfolio,
        prices,
        state,
        now=now,
        price_times=price_times,
    )
    row = res['results'][0]
    if row['verdict'] == 'PASS':
        max_loss = row.get('max_loss') or 0.0
        risk_cents = int(Decimal(str(max_loss)) * fx * 100)
        return {
            'decision': 'paper_allowed',
            'reject_code': None,
            'risk_amount_cents': risk_cents,
            'upstream_fingerprint': row.get('fingerprint'),
        }
    reason = (row.get('reasons') or ['RISK_BLOCK'])[0]
    code = reason.split(':', 1)[0].strip().replace(' ', '_').upper()[:64]
    return {'decision': 'rejected', 'reject_code': code or 'RISK_BLOCK', 'risk_amount_cents': 0}
