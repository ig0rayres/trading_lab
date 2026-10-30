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
       'orders_sent':0,'limitations':['P&L excludes fees/slippage','Only recorded snapshots are counted',
           'No provider performance inferred from shadow candidates',
           'Postgres ledger is audit trail; broker_reconciled stays false until operator homologation']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='/app/reports');parser.add_argument('--output')
    args=parser.parse_args();d=summary(Path(args.root))
    if args.output:
        p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2))
    print(json.dumps(d,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
