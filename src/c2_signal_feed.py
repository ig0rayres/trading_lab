"""Collective2 read-only active-order watcher. Does NOT synthesize executable tickets.

A strategy's active order is not proof of a new, subscriber-licensed signal,
protective stop or fill. Poll snapshots; review changes and subscription rights.
"""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib import parse, request, error

BASE='https://api4-general.collective2.com'
ENDPOINT='/Strategies/GetStrategyActiveOrders'


def fetch_orders(strategy_ids, key, opener=request.urlopen):
    if not key or not strategy_ids:
        raise ValueError('missing API key or strategy IDs')
    params=parse.urlencode([('StrategyIds',str(x)) for x in strategy_ids])
    req=request.Request(BASE+ENDPOINT+'?'+params,headers={
        'Authorization':'Bearer '+key,'Accept':'application/json',
        'User-Agent':'TradingLab-C2-ReadOnly/1.0'})
    with opener(req,timeout=25) as response:
        obj=json.load(response)
    if not isinstance(obj,dict) or not isinstance(obj.get('Results'),list):
        raise ValueError('invalid API response')
    status=obj.get('ResponseStatus') or {}
    if str(status.get('ErrorCode','200')) not in ('200','0','None') or status.get('Errors'):
        raise ValueError('API reported failure')
    return obj['Results']


def sanitized_record(row):
    if not isinstance(row,dict):raise ValueError('bad order row')
    # Keep only fields that are useful for read-only diagnostics; never infer a protective stop.
    allow=('Id','StrategyId','SignalId','OrderId','OrderStatus','SignalType','OrderType',
           'PostedDate','CreatedDate','Quantity','FilledQuantity','AvgFillPrice',
           'LimitPrice','StopPrice','Action','BuySell','Side','C2Symbol','ExchangeSymbol')
    return {k:row[k] for k in allow if k in row}


def identity(row):
    # Content fingerprint is stable across poll rounds for unchanged active orders.
    return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]


def snapshot(ids, key, output_dir, opener=request.urlopen, now=None):
    now=now or datetime.now(timezone.utc)
    base=Path(output_dir)
    rows=[sanitized_record(x) for x in fetch_orders(ids,key,opener)]
    current={identity(x):x for x in rows}
    base.mkdir(parents=True,exist_ok=True)
    path=base/'active-orders-latest.json'
    previous={}
    if path.exists():
        old=json.loads(path.read_text())
        if isinstance(old.get('records'),list): previous={identity(x):x for x in old['records']}
    new_ids=sorted(set(current)-set(previous))
    gone_ids=sorted(set(previous)-set(current))
    # First observation is a baseline: no signal classified as new.
    first=not path.exists()
    report={'mode':'C2_ACTIVE_ORDERS_READ_ONLY','as_of':now.isoformat(),
            'strategy_ids':ids,'records':list(current.values()),
            'first_snapshot':first,'new_or_changed':[current[x] for x in new_ids] if not first else [],
            'missing_since_last':[previous[x] for x in gone_ids] if not first else [],
            'orders_sent':0,'execution_authorized':False,
            'warning':'Active orders are NOT executable trade signals. Requires subscription access, price verification, explicit stop, and risk controls.'}
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w',dir=base,delete=False,prefix='.c2-',suffix='.json') as f:
        json.dump(report,f,indent=2); temp=f.name
    os.replace(temp,path)
    return {k:v for k,v in report.items() if k not in ('records','new_or_changed','missing_since_last')} | {
        'active_orders':len(rows),'new_or_changed_count':len(report['new_or_changed']),
        'missing_count':len(report['missing_since_last']), 'report_file':str(path)}


def main():
    p=argparse.ArgumentParser(description='Poll Collective2 active strategy orders (read only; not tradable signals)')
    p.add_argument('--strategy-id',type=int,action='append',required=True)
    p.add_argument('--output-dir',default='/app/reports/providers/signals')
    args=p.parse_args()
    if any(i<=0 for i in args.strategy_id):p.error('strategy IDs must be positive')
    try:
        result=snapshot(sorted(set(args.strategy_id)),os.environ.get('C2_API4_KEY',''),args.output_dir)
        print(json.dumps(result,indent=2));return 0
    except (ValueError,OSError,error.HTTPError,error.URLError) as exc:
        print(json.dumps({'status':'BLOCKED','error_type':type(exc).__name__,'orders_sent':0}));return 2

if __name__=='__main__':raise SystemExit(main())
