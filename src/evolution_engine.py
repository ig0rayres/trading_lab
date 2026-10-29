"""Daily read-only review. No broker access, order execution, or strategy mutation."""
import argparse
import csv
import fcntl
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(os.environ.get('EVOLUTION_DIR', '/app/reports/evolution'))
WEBHOOK_ROOT = Path(os.environ.get('TV_QUEUE_DIR', '/app/reports/webhooks/pending')).parent


def utc(value):
    result = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp must have timezone')
    return result.astimezone(timezone.utc)


def jsonl(path):
    if not path.exists():
        return []
    records = []
    for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            if isinstance(record, dict):
                records.append(record)
        except (json.JSONDecodeError, TypeError):
            # An incomplete append must not erase the rest of the day's evidence.
            pass
    return records


def add_decision(path, payload):
    # Append-only event ledger; no fabricated performance metrics.
    status = payload.get('decision')
    if status not in ('ACCEPTED', 'REJECTED', 'OBSERVED'):
        raise ValueError('decision must be ACCEPTED, REJECTED, or OBSERVED')
    sid = payload.get('signal_id')
    if not isinstance(sid, str) or not 6 <= len(sid) <= 128:
        raise ValueError('signal_id invalid')
    stamp = utc(payload['at'])
    row = {'at': stamp.isoformat(), 'signal_id': sid,
           'strategy_id': str(payload.get('strategy_id', 'unknown'))[:100],
           'symbol': str(payload.get('symbol', 'unknown'))[:30],
           'decision': status, 'reason': str(payload.get('reason', ''))[:250],
           'policy_version': str(payload.get('policy_version', 'unversioned'))[:100]}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    return row


def review(day, root=ROOT, webhook_root=WEBHOOK_ROOT):
    start = datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    journal = [r for r in jsonl(webhook_root / 'journal.jsonl')
               if 'at' in r and start <= utc(r['at']) < end]
    decisions = [r for r in jsonl(root / 'decisions.jsonl')
                 if 'at' in r and start <= utc(r['at']) < end]
    outcome_rows = [r for r in jsonl(root / 'outcomes.jsonl')
                    if 'at' in r and start <= utc(r['at']) < end]
    statuses = Counter(str(r.get('result', {}).get('status', 'UNKNOWN')) for r in journal)
    reasons = Counter(str(reason) for r in journal
                      for reason in r.get('result', {}).get('reasons', []))
    choices = Counter(str(r.get('decision')) for r in decisions)
    by_strategy = defaultdict(lambda: Counter())
    for record in decisions:
        by_strategy[record['strategy_id']][record['decision']] += 1
    recommendations = []
    if not decisions:
        recommendations.append('Instrument decision capture BEFORE the entry filters; rejected opportunities are currently invisible.')
    if journal and not outcome_rows:
        recommendations.append('No independently measured outcome data: cannot score win rate, avoided losses, or profitability.')
    if reasons:
        recommendations.append('Inspect recurring blocked reasons; remove only filters that underperform in out-of-sample shadow tests.')
    if choices['REJECTED'] and not outcome_rows:
        recommendations.append('Follow rejected signals with time-stamped market data and realistic fees/slippage before claiming missed opportunity.')
    if not journal and not decisions:
        recommendations.append('No observed signals for this date: do not infer strategy quality from an empty sample.')
    report = {
        'schema_version': 'evolution-1', 'date_utc': day,
        'mode': 'READ_ONLY_NO_ORDER_SUBMISSION',
        'webhook_processed': len(journal), 'worker_statuses': dict(statuses),
        'worker_block_reasons': dict(reasons),
        'decision_events': len(decisions), 'decisions': dict(choices),
        'by_strategy': {k: dict(v) for k,v in sorted(by_strategy.items())},
        'labeled_outcomes': len(outcome_rows),
        'performance_metrics_available': False,
        'reason_performance': 'Outcome schema and independent market-price labeling not yet validated',
        'recommendations': recommendations,
        'changes_applied': 0, 'orders_sent': 0,
        'data_limitations': ['Webhook journal records worker processing, not all market opportunities.',
                             'Rejected signals are visible only if an upstream producer records decision events.',
                             'Preview orders are not executed trades.',
                             'No price-path simulation, out-of-sample test, or statistically valid promotion in this build.']
    }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument('--record-decision', help='Path to one JSON event (no credentials)')
    parser.add_argument('--output-dir', default=str(ROOT))
    args = parser.parse_args()
    root = Path(args.output_dir)
    if args.record_decision:
        event = json.loads(Path(args.record_decision).read_text(encoding='utf-8'))
        print(json.dumps(add_decision(root / 'decisions.jsonl', event), ensure_ascii=False))
        return
    report = review(args.date, root)
    out = root / 'daily' / (args.date + '.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix('.tmp')
    tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(out)
    print(json.dumps({'report_path': str(out), 'summary': report}, ensure_ascii=False))

if __name__ == '__main__':
    main()
