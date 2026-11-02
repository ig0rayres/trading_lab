"""Read-only event aggregation for dashboard; missing data is unknown, never profit."""
import argparse
import json
import os
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

def read_jsonl(path):
    if not path.exists(): return []
    rows=[]
    for line in path.read_text().splitlines():
        try:
            x=json.loads(line)
            if isinstance(x,dict):rows.append(x)
        except (ValueError,TypeError):pass
    return rows

def _load_prodigy_opportunities(root):
    path = Path(root) / 'intelligence' / 'prodigy-top10-latest.json'
    if not path.is_file():
        return {'status': 'NOT_RUN', 'items': [], 'disclaimer': 'Research rank only; does not authorize orders.'}
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return {'status': 'UNREADABLE', 'items': [], 'disclaimer': 'Research rank only; does not authorize orders.'}
    if not isinstance(payload, dict) or payload.get('mode') != 'PRODIGY_RANK_RESEARCH_ONLY':
        return {'status': 'UNTRUSTED', 'items': [], 'disclaimer': 'Research rank only; does not authorize orders.'}
    top = payload.get('top_10_research') or payload.get('providers') or []
    items = []
    for row in top[:10]:
        if not isinstance(row, dict):
            continue
        items.append(
            {
                'provider': row.get('provider'),
                'status': row.get('status'),
                'prodigy_score': row.get('prodigy_score'),
                'label': 'research_tip',
            }
        )
    return {
        'status': 'OK',
        'as_of': payload.get('as_of'),
        'items': items,
        'disclaimer': str(payload.get('score_warning') or 'Research rank only; does not authorize orders.'),
        'execution_authorized': False,
    }

def _load_evolution_recent(root, limit=8):
    rows = read_jsonl(Path(root) / 'evolution' / 'decisions.jsonl')
    recent = []
    for row in rows[-limit:]:
        if not isinstance(row, dict):
            continue
        recent.append(
            {
                'at': row.get('at') or row.get('timestamp'),
                'kind': row.get('kind') or row.get('decision'),
                'summary': row.get('summary') or row.get('note'),
                'label': 'continuous_improvement',
            }
        )
    return {'count': len(rows), 'recent': recent}

def _load_strategy_catalog():
    try:
        from strategy_catalog import list_strategy_states

        rows = list_strategy_states()
    except ImportError:
        rows = None
    if rows is None:
        return {'status': 'LEDGER_UNAVAILABLE', 'strategies': []}
    return {'status': 'OK', 'strategies': rows, 'note': 'Phase changes are operator-only; dashboard is read-only.'}

def command_panel(root):
    root = Path(root)
    ledger = None
    try:
        from ledger_reconcile import ledger_snapshot

        ledger = ledger_snapshot()
    except ImportError:
        ledger = None
    fills = 0
    if isinstance(ledger, dict):
        fills = int(ledger.get('paper_fills') or 0)
    queued = int(ledger.get('paper_queued_intent') or 0) if isinstance(ledger, dict) else 0
    return {
        'schema_version': 'command-panel-v1',
        'financial_health': {
            'ledger_connected': isinstance(ledger, dict) and ledger.get('status') != 'LEDGER_UNAVAILABLE',
            'paper_fills_recorded': fills,
            'paper_queued_intent': queued,
            'queued_is_not_fill': queued > 0 and fills == 0,
            'performance_credibility': 'verified_fills' if fills > 0 else 'awaiting_operator_homologation',
        },
        'strategy_catalog': _load_strategy_catalog(),
        'opportunities': _load_prodigy_opportunities(root),
        'continuous_improvement': _load_evolution_recent(root),
        'history': {'postgres_ledger_counts': ledger},
    }

def summary(root):
    root=Path(root)
    snaps=read_jsonl(root/'paper/order-snapshots.jsonl')
    latest={}
    for s in snaps:
        key=s.get('client_order_id')
        if key and s.get('status')=='MONITORED': latest[key]=s
    closed=[];open_count=0
    for s in latest.values():
        try:
            entry=Decimal(str(s.get('entry_qty') or 0));remaining=Decimal(str(s.get('remaining_qty') or 0))
            if entry>0 and remaining==0:closed.append(Decimal(str(s['realized_gross_pnl_usd'])))
            elif entry>0: open_count+=1
        except (InvalidOperation,KeyError):continue
    journal=read_jsonl(root/'webhooks/journal.jsonl')
    decisions=read_jsonl(root/'evolution/decisions.jsonl')
    statuses=Counter(str(x.get('result',{}).get('status','UNKNOWN')) for x in journal)
    ledger = None
    try:
        from ledger_reconcile import ledger_snapshot

        ledger = ledger_snapshot()
    except ImportError:
        ledger = None
    shadow = {
        'decision_events': len(decisions),
        'webhook_journal_events': len(journal),
        'worker_statuses': dict(statuses),
    }
    paper = {
        'orders_monitored': len(latest),
        'positions_open': open_count,
        'closed_with_pnl': len(closed),
    }
    return {'schema_version':'trading-dashboard-v4','mode':'READ_ONLY','currency':'USD',
       'paper_orders_monitored':len(latest),'positions_not_fully_closed':open_count,
       'closed_orders_with_pnl':len(closed),
       'realized_gross_pnl_usd':str(sum(closed,Decimal(0))) if closed else None,
       'pnl_unavailable_reason':None if closed else 'NO_CLOSED_MONITORED_ORDERS',
       'journal_events':len(journal),'worker_statuses':dict(statuses),
       'decision_events':len(decisions), 'win_rate':None if not closed else sum(x>0 for x in closed)/len(closed),
       'shadow_vs_paper': {'shadow': shadow, 'paper_snapshots': paper, 'postgres_ledger': ledger},
       'command_panel': command_panel(root),
       'orders_sent':0,'limitations':['P&L excludes fees/slippage','Only recorded snapshots are counted',
           'No provider performance inferred from shadow candidates',
           'Postgres ledger is audit trail; broker_reconciled stays false until operator homologation',
           'Prodigy opportunities and evolution entries are research tips, not trade instructions',
           'Strategy phases shown here cannot be changed from the dashboard']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='/app/reports');parser.add_argument('--output')
    args=parser.parse_args();d=summary(Path(args.root))
    if args.output:
        p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2))
    print(json.dumps(d,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
