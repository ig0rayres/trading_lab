"""Append-only, tamper-evident, offline Shadow outcome journal.

This records only HYPOTHETICAL evaluations of local unfilled intents. It never
sends broker orders or asserts an actual fill. A hash chain detects accidental
modification or removal of any *non-tail* journal entry; external anchoring is
required to detect full-file replacement or tail truncation.
"""
import argparse
import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from v4_shadow_marks import evaluate_shadow

ZERO = '0' * 64
STATES = {'HYPOTHETICAL_STOP', 'HYPOTHETICAL_TARGET', 'HYPOTHETICAL_OPEN', 'HYPOTHETICAL_PENDING'}


def canonical(record):
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(record):
    return hashlib.sha256(canonical(record).encode('utf-8')).hexdigest()


def verify(path):
    path = Path(path)
    if not path.exists():
        return {'valid': True, 'events': 0, 'last_hash': ZERO, 'signal_ids': set()}
    previous = ZERO
    seen = set()
    total = 0
    try:
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                if not line.strip():
                    raise ValueError('EMPTY_LINE')
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError('INVALID_RECORD')
                claim = record.pop('hash', None)
                if record.get('previous_hash') != previous or claim != digest(record):
                    raise ValueError('CHAIN_MISMATCH')
                if record.get('schema_version') != 1 or record.get('event') != 'SHADOW_EVALUATED':
                    raise ValueError('UNEXPECTED_EVENT')
                signal = record.get('signal_key')
                if not isinstance(signal, str) or not signal or signal in seen:
                    raise ValueError('DUPLICATE_OR_MISSING_SIGNAL')
                if record.get('result', {}).get('broker_filled') is not False or record['result'].get('status') not in STATES:
                    raise ValueError('NOT_HYPOTHETICAL')
                seen.add(signal)
                previous = claim
                total += 1
    except (ValueError, TypeError, KeyError, json.JSONDecodeError, UnicodeError) as exc:
        return {'valid': False, 'events': total, 'error': str(exc)}
    return {'valid': True, 'events': total, 'last_hash': previous, 'signal_ids': seen}


def append_evaluation(intent, bars, *, target_brl, ledger, fee_brl='0', slippage_brl='0', now=None):
    if os.environ.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        return {'status': 'BLOCKED', 'reason': 'LIVE_TRADING_NOT_DISABLED', 'orders_sent': 0}
    try:
        if not isinstance(intent, dict):
            raise ValueError('INVALID_INTENT')
        key_parts = [intent.get(x) for x in ('market', 'strategy_id', 'signal_id')]
        if any(not isinstance(x, str) or not x.strip() for x in key_parts):
            raise ValueError('INVALID_IDENTITY')
        if intent['market'] not in {'B3_EQUITY', 'CRYPTO'}:
            raise ValueError('INVALID_MARKET')
        result = evaluate_shadow(intent, bars, target_brl=target_brl, fee_brl=fee_brl, slippage_brl=slippage_brl)
        if result.get('broker_filled') is not False or result['status'] not in STATES:
            raise ValueError('INVALID_RESULT')
        signal_key = digest({'market': key_parts[0], 'strategy_id': key_parts[1], 'signal_id': key_parts[2]})
        ledger = Path(ledger)
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.with_suffix(ledger.suffix + '.lock').open('a+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            chain = verify(ledger)
            if not chain['valid']:
                raise ValueError('JOURNAL_INTEGRITY_FAILED')
            if signal_key in chain['signal_ids']:
                return {'status': 'BLOCKED', 'reason': 'ALREADY_EVALUATED', 'orders_sent': 0}
            timestamp = now or datetime.now(timezone.utc)
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError('NAIVE_TIMESTAMP')
            record = {'schema_version': 1, 'event': 'SHADOW_EVALUATED', 'signal_key': signal_key,
                      'market': key_parts[0], 'strategy_id': key_parts[1], 'signal_id': key_parts[2],
                      'at_utc': timestamp.astimezone(timezone.utc).isoformat(),
                      'previous_hash': chain['last_hash'], 'result': result,
                      'data_provenance': 'CALLER_VERIFIED_NOT_INDEPENDENTLY_ATTESTED'}
            record['hash'] = digest(record)
            with ledger.open('a', encoding='utf-8') as stream:
                stream.write(canonical(record) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            return {'status': 'SHADOW_EVALUATION_RECORDED', 'hash': record['hash'],
                    'hypothetical_status': result['status'], 'orders_sent': 0}
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as exc:
        return {'status': 'BLOCKED', 'reason': f'INVALID_INPUT_OR_LEDGER:{type(exc).__name__}', 'orders_sent': 0}


def report(path):
    chain = verify(path)
    if not chain['valid']:
        return {'mode': 'SHADOW_ONLY', 'integrity': 'FAILED', 'error': chain['error'], 'broker_fills': None}
    counts = {state: 0 for state in sorted(STATES)}
    total_pnl = 0
    from decimal import Decimal
    total_pnl = Decimal(0)
    with Path(path).open(encoding='utf-8') if Path(path).exists() else __import__('io').StringIO('') as stream:
        for line in stream:
            result = json.loads(line)['result']
            counts[result['status']] += 1
            if result['status'] in {'HYPOTHETICAL_STOP', 'HYPOTHETICAL_TARGET'}:
                total_pnl += Decimal(result['hypothetical_net_pnl_brl'])
    return {'mode': 'SHADOW_ONLY', 'integrity': 'VERIFIED_LOCAL_CHAIN', 'events': chain['events'],
            'outcomes': counts, 'hypothetical_closed_net_pnl_brl': str(total_pnl),
            'broker_fills': 0, 'live_execution': False,
            'limitations': ['Not broker P&L', 'No independent price verification', 'No external hash anchoring']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ledger', default='/app/reports/shadow/v4-outcomes.jsonl')
    args = parser.parse_args()
    result = report(args.ledger)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['integrity'] != 'FAILED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
