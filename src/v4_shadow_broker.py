"""Local-only B3/crypto Paper simulator. No network/broker submission.

Execution is deliberately conservative: entries are recorded as requested,
not filled. A separate trusted market-data fill engine is required to convert
orders to fills. The simulator does not assert P&L from requested entries.
"""
import argparse
import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from portfolio_risk_v4 import evaluate, number

MARKETS = {'B3_EQUITY', 'CRYPTO'}


def _canonical(ticket):
    fields = ('market', 'symbol', 'side', 'quantity', 'entry_brl', 'stop_brl', 'strategy_id', 'signal_id')
    return json.dumps({k: ticket.get(k) for k in fields}, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def _check_ticket(ticket):
    if not isinstance(ticket, dict):
        raise ValueError('INVALID_TICKET')
    if ticket.get('market') not in MARKETS:
        raise ValueError('ONLY_B3_OR_CRYPTO_SHADOW')
    for key in ('strategy_id', 'signal_id'):
        if not isinstance(ticket.get(key), str) or not ticket[key].strip():
            raise ValueError('MISSING_SIGNAL_IDENTITY')
    if ticket.get('verified') is not True or ticket.get('trading_mode') != 'PAPER':
        raise ValueError('UNVERIFIED_OR_NOT_PAPER')
    if ticket.get('side') != 'buy':
        raise ValueError('LONG_ONLY')
    # Do not trust float quantities/money. Decimal-safe validation happens in evaluate.
    for key in ('quantity', 'entry_brl', 'stop_brl'):
        number(ticket[key])


def submit_local(ticket, snapshot, ledger, *, now=None):
    """Reserve a Paper intent atomically. Never imply a fill or send an order."""
    if os.environ.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        return {'status': 'BLOCKED', 'reasons': ['LIVE_TRADING_NOT_DISABLED'], 'orders_sent': 0}
    try:
        _check_ticket(ticket)
        if not isinstance(snapshot, dict):
            raise ValueError('INVALID_SNAPSHOT')
        ledger = Path(ledger)
        ledger.parent.mkdir(parents=True, exist_ok=True)
        fingerprint = hashlib.sha256(_canonical(ticket).encode('utf-8')).hexdigest()[:24]
        # Lock and inspect journal before evaluating snapshot: no second intent even if stale state.
        with ledger.with_suffix('.lock').open('a+') as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            if ledger.exists():
                for line in ledger.read_text(encoding='utf-8').splitlines():
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    if record.get('fingerprint') == fingerprint or (
                        record.get('market') == ticket['market'] and
                        record.get('signal_id') == ticket['signal_id'] and
                        record.get('strategy_id') == ticket['strategy_id']
                    ):
                        return {'status': 'BLOCKED', 'reasons': ['DUPLICATE_PAPER_INTENT'], 'orders_sent': 0}
            decision = evaluate(ticket, snapshot)
            if not decision['allowed']:
                return {'status': 'BLOCKED', 'reasons': decision['reasons'], 'orders_sent': 0}
            event = {
                'schema_version': 1,
                'event': 'PAPER_ENTRY_REQUESTED_NOT_FILLED',
                'at_utc': (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat(),
                'fingerprint': fingerprint,
                'market': ticket['market'],
                'symbol': ticket['symbol'].strip().upper(),
                'strategy_id': ticket['strategy_id'],
                'signal_id': ticket['signal_id'],
                'quantity': str(number(ticket['quantity'])),
                'entry_brl': str(number(ticket['entry_brl'])),
                'stop_brl': str(number(ticket['stop_brl'])),
                'status': 'PENDING_VERIFIED_MARKET_FILL',
                'source': 'LOCAL_SIMULATOR_NO_BROKER',
            }
            with ledger.open('a', encoding='utf-8') as output:
                output.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + '\n')
                output.flush()
                os.fsync(output.fileno())
            return {'status': 'PAPER_INTENT_RECORDED_NOT_FILLED', 'fingerprint': fingerprint,
                    'orders_sent': 0, 'broker_orders_sent': 0}
    except (ValueError, TypeError, KeyError, OSError, json.JSONDecodeError) as exc:
        return {'status': 'BLOCKED', 'reasons': [f'INVALID_INPUT_OR_JOURNAL:{type(exc).__name__}'], 'orders_sent': 0}


def main():
    parser = argparse.ArgumentParser(description='Create local-only paper intent; NOT an actual fill')
    parser.add_argument('--ticket', required=True)
    parser.add_argument('--verified-snapshot', required=True)
    parser.add_argument('--ledger', default='/app/reports/paper/v4-local-intents.jsonl')
    args = parser.parse_args()
    try:
        ticket = json.loads(Path(args.ticket).read_text(encoding='utf-8'))
        snapshot = json.loads(Path(args.verified_snapshot).read_text(encoding='utf-8'))
        result = submit_local(ticket, snapshot, args.ledger)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {'status': 'BLOCKED', 'reasons': [type(exc).__name__], 'orders_sent': 0}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] == 'PAPER_INTENT_RECORDED_NOT_FILLED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
