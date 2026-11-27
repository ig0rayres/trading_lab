"""Daily read-only review. No broker access, order execution, or strategy mutation."""
import argparse
import fcntl
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from panel_ops_data import read_jsonl, signal_destination
from timesfm_context import build_timesfm_block

ROOT = Path(os.environ.get('EVOLUTION_DIR', '/app/reports/evolution'))
WEBHOOK_ROOT = Path(os.environ.get('TV_QUEUE_DIR', '/app/reports/webhooks/pending')).parent

TIP_LABELS = frozenset({'research_tip', 'suggestion', 'continuous_improvement'})
FILL_SNAPSHOT_STATUSES = frozenset({'filled', 'partially_filled', 'MONITORED'})


def utc(value):
    result = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp must have timezone')
    return result.astimezone(timezone.utc)


def jsonl(path):
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding='utf-8').splitlines():
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


def _reports_root(webhook_root: Path, evolution_root: Path) -> Path:
    if evolution_root.name == 'evolution' and evolution_root.parent != evolution_root:
        return evolution_root.parent
    return webhook_root.parent


def _load_paper_snapshots(webhook_root: Path, evolution_root: Path, start, end) -> list[dict]:
    paper = _reports_root(webhook_root, evolution_root) / 'paper' / 'order-snapshots.jsonl'
    rows = []
    for row in read_jsonl(paper):
        ts = row.get('at') or row.get('updated_at') or row.get('timestamp')
        if not ts:
            continue
        try:
            if start <= utc(ts) < end:
                rows.append(row)
        except (ValueError, TypeError):
            continue
    return rows


def _classify_day(journal, decisions, snapshots):
    fills = []
    non_fills = []
    seen_keys: set[str] = set()

    def _key(prefix: str, item: dict) -> str:
        return prefix + ':' + str(item.get('signal_id') or item.get('client_order_id') or item.get('at'))

    for record in journal:
        res = record.get('result') or {}
        dest = signal_destination(
            event_status=record.get('event_status'),
            reject_code=res.get('reject_code'),
            paper_status=res.get('paper_status'),
            gateway_status=res.get('gateway_status'),
        )
        status = str(res.get('status', 'UNKNOWN'))
        strategy_id = str(record.get('strategy_id') or res.get('strategy_id') or 'unknown')
        item = {
            'source': 'webhook_journal',
            'destination': dest,
            'worker_status': status,
            'strategy_id': strategy_id,
            'symbol': record.get('symbol') or res.get('symbol'),
        }
        k = _key('j', item)
        if k in seen_keys:
            continue
        seen_keys.add(k)
        if dest == 'order':
            fills.append(item)
        else:
            non_fills.append(item)

    for record in decisions:
        decision = str(record.get('decision', ''))
        item = {
            'source': 'decision_event',
            'decision': decision,
            'strategy_id': str(record.get('strategy_id', 'unknown')),
            'symbol': record.get('symbol'),
            'reason': record.get('reason'),
        }
        k = _key('d', record)
        if k in seen_keys:
            continue
        seen_keys.add(k)
        if decision == 'REJECTED':
            non_fills.append(item)
        elif decision == 'ACCEPTED':
            fills.append(item)

    for snap in snapshots:
        status = str(snap.get('status', ''))
        broker = str(snap.get('broker_status', ''))
        confirmed = bool(snap.get('broker_fill_confirmed'))
        dest = signal_destination(
            event_status=snap.get('event_status'),
            paper_status=status or broker,
            gateway_status=snap.get('gateway_status'),
        )
        item = {
            'source': 'paper_snapshot',
            'destination': dest,
            'status': status,
            'strategy_id': str(snap.get('strategy_key') or snap.get('strategy_id') or 'unknown'),
            'client_order_id': snap.get('client_order_id'),
            'broker_fill_confirmed': confirmed,
        }
        k = _key('s', snap)
        if k in seen_keys:
            continue
        seen_keys.add(k)
        if confirmed or status in FILL_SNAPSHOT_STATUSES and dest == 'order':
            fills.append(item)
        elif dest != 'order':
            non_fills.append(item)

    return fills, non_fills


def _tip_shell(label: str, summary: str, *, kind: str, strategy_id: str | None = None) -> dict:
    if label not in TIP_LABELS:
        label = 'suggestion'
    row = {
        'label': label,
        'kind': kind,
        'summary': summary[:500],
        'execution_authorized': False,
        'paper_allowed': False,
        'orders_sent': 0,
    }
    if strategy_id:
        row['strategy_id'] = strategy_id
    return row


def _build_labeled_tips(fills, non_fills, journal, decisions, recommendations):
    tips = []
    if not journal and not decisions and not fills and not non_fills:
        tips.append(_tip_shell(
            'suggestion',
            'No observed signals for this date: do not infer strategy quality from an empty sample.',
            kind='empty_sample',
        ))
    for item in fills:
        sid = item.get('strategy_id', 'unknown')
        tips.append(_tip_shell(
            'research_tip',
            f'Confirmed execution path for strategy {sid} ({item.get("source")}): review outcome labeling before promotion.',
            kind='fill',
            strategy_id=sid,
        ))
    for item in non_fills:
        sid = item.get('strategy_id', 'unknown')
        reason = item.get('reason') or item.get('worker_status') or item.get('decision')
        tips.append(_tip_shell(
            'suggestion',
            f'Non-execution for strategy {sid} ({item.get("source")}): {reason or "blocked or queued without fill"}.',
            kind='non_fill',
            strategy_id=sid,
        ))
    for text in recommendations:
        tips.append(_tip_shell('continuous_improvement', text, kind='legacy_recommendation'))
    return tips


def _series_from_journal(journal) -> list[float]:
    series = []
    for row in journal:
        res = row.get('result') or {}
        for key in ('fill_qty', 'qty', 'score'):
            if key in res:
                try:
                    series.append(float(res[key]))
                except (TypeError, ValueError):
                    pass
                break
        else:
            series.append(float(len(series) + 1))
    return series[-64:]


def review(day, root=ROOT, webhook_root=WEBHOOK_ROOT, context_providers=None):
    start = datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    journal = [r for r in jsonl(webhook_root / 'journal.jsonl')
               if 'at' in r and start <= utc(r['at']) < end]
    decisions = [r for r in jsonl(root / 'decisions.jsonl')
                 if 'at' in r and start <= utc(r['at']) < end]
    outcome_rows = [r for r in jsonl(root / 'outcomes.jsonl')
                    if 'at' in r and start <= utc(r['at']) < end]
    snapshots = _load_paper_snapshots(webhook_root, root, start, end)

    statuses = Counter(str(r.get('result', {}).get('status', 'UNKNOWN')) for r in journal)
    reasons = Counter(str(reason) for r in journal
                      for reason in r.get('result', {}).get('reasons', []))
    choices = Counter(str(r.get('decision')) for r in decisions)
    by_strategy = defaultdict(lambda: Counter())
    for record in decisions:
        by_strategy[record['strategy_id']][record['decision']] += 1

    fills, non_fills = _classify_day(journal, decisions, snapshots)

    recommendations = []
    if not decisions:
        recommendations.append(
            'Instrument decision capture BEFORE the entry filters; rejected opportunities are currently invisible.'
        )
    if journal and not outcome_rows:
        recommendations.append(
            'No independently measured outcome data: cannot score win rate, avoided losses, or profitability.'
        )
    if reasons:
        recommendations.append(
            'Inspect recurring blocked reasons; remove only filters that underperform in out-of-sample shadow tests.'
        )
    if choices['REJECTED'] and not outcome_rows:
        recommendations.append(
            'Follow rejected signals with time-stamped market data and realistic fees/slippage before claiming missed opportunity.'
        )
    if not journal and not decisions:
        recommendations.append('No observed signals for this date: do not infer strategy quality from an empty sample.')

    tips = _build_labeled_tips(fills, non_fills, journal, decisions, recommendations)

    providers = list(context_providers) if context_providers is not None else [build_timesfm_block]
    timesfm_payload = {'timesfm_status': 'UNAVAILABLE', 'tips': []}
    context_series = _series_from_journal(journal)
    for provider in providers:
        block = provider(day=day, context_values=context_series)
        if block.get('timesfm_status') == 'OK':
            timesfm_payload = block
            tips.extend(block.get('tips') or [])
        elif block.get('timesfm_status'):
            timesfm_payload = {
                'timesfm_status': block.get('timesfm_status', 'UNAVAILABLE'),
                'note': block.get('note'),
                'tips': [],
            }

    report = {
        'schema_version': 'evolution-1', 'date_utc': day,
        'mode': 'READ_ONLY_NO_ORDER_SUBMISSION',
        'webhook_processed': len(journal), 'worker_statuses': dict(statuses),
        'worker_block_reasons': dict(reasons),
        'decision_events': len(decisions), 'decisions': dict(choices),
        'by_strategy': {k: dict(v) for k, v in sorted(by_strategy.items())},
        'labeled_outcomes': len(outcome_rows),
        'performance_metrics_available': False,
        'reason_performance': 'Outcome schema and independent market-price labeling not yet validated',
        'recommendations': recommendations,
        'execution_summary': {
            'fills_observed': len(fills),
            'non_fills_observed': len(non_fills),
            'paper_snapshots_in_day': len(snapshots),
        },
        'tips': tips,
        'timesfm': timesfm_payload,
        'changes_applied': 0, 'orders_sent': 0,
        'supervised_adjustments': {
            'mode': 'PROPOSAL_ONLY',
            'label': 'continuous_improvement',
            'execution_authorized': False,
            'paper_allowed': False,
            'orders_sent': 0,
            'note': 'Parameter apply/undo via Central /api/strategy-parameters; never mutates risk anchors.',
        },
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