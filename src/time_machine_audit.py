#!/usr/bin/env python3
"""Bounded, read-only cross-check using upstream trader-timemachine unmodified."""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

from original import load_original

NY=ZoneInfo('America/New_York')

def choose(rows, limit, target):
    xs=[r for r in rows if int(float(r['target_r']))==target]
    xs.sort(key=lambda r:(r['date'],r['symbol']),reverse=True)
    return xs[:limit]

def audit(args):
    orig=load_original(args.repo)
    script=Path(orig.path)/'trader-timemachine'/'timemachine.py'
    if not script.is_file():raise RuntimeError('Missing original trader-timemachine/timemachine.py')
    folder=Path(args.history).resolve()
    csvfile=folder/'trades.csv'
    if not csvfile.is_file():raise RuntimeError('Missing historical trades.csv; run history first')
    with csvfile.open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
    chosen=choose(rows,args.limit,args.target)
    if not chosen:raise RuntimeError('No historical trades for this target')
    output=Path(args.output or folder/'timemachine-audit')
    output.mkdir(parents=True,exist_ok=True)
    results=[]
    for r in chosen:
        sym=r['symbol']; date=r['date']
        cache=list((folder/'cache').glob(sym.replace('.','-')+'-*.json'))
        if args.offline_dir:
            cache=[Path(args.offline_dir)/(sym+'.json')]
        if not cache or not cache[0].is_file():
            results.append({'symbol':sym,'date':date,'status':'SKIPPED','reason':'RAW_CHART_NOT_FOUND'});continue
        # Original API's entry-time represents the bar CLOSE; our entry_at
        # represents the next bar OPEN: same wall clock by design.
        tm_args=[sys.executable,str(script),'run','--symbol',sym,'--date',date,
                 '--entry',r['entry_fill'],'--stop',r['stop'],'--target',r['target'],
                 '--entry-time',dt.datetime.fromisoformat(r['entry_at']).strftime('%H:%M'),
                 '--stop-rule','or_mid','--replays',str(args.replays),
                 '--seed',str(args.seed),'--offline',str(cache[0]),'--json',
                 '--now',date+' 16:30']
        run=subprocess.run(tm_args,capture_output=True,text=True,timeout=120,check=False)
        if run.returncode:
            results.append({'symbol':sym,'date':date,'status':'SKIPPED',
                            'reason':'UPSTREAM_REFUSED','details':run.stderr[-600:]});continue
        try:doc=json.loads(run.stdout)
        except ValueError:
            results.append({'symbol':sym,'date':date,'status':'ERROR','reason':'BAD_UPSTREAM_OUTPUT'});continue
        name=f'{date}-{sym}-{args.target}R.json'
        (output/name).write_text(json.dumps(doc,indent=2)+'\n',encoding='utf8')
        h=doc.get('history') or {};mc=doc.get('mc') or {}
        results.append({'symbol':sym,'date':date,'status':'OK','trading_lab_net_r':float(r['net_r']),
                        'upstream_mc_avg_r':mc.get('avg_R'),'upstream_history_avg_r':h.get('avg_R'),
                        'upstream_history_triggered':h.get('triggered'),'upstream_replays':mc.get('replays'),
                        'upstream_report':name})
    summary={'status':'DIAGNOSTIC_ONLY_NOT_COMPARABLE_PNL','upstream_commit':orig.commit,
             'source_history':str(folder),'target_r':args.target,'requested':len(chosen),
             'completed':sum(x['status']=='OK' for x in results),'results':results,
             'warnings':['Monte Carlo trajectories are not independent historical sessions.',
                         'Upstream Time Machine uses a different replay and cost model; its R and Trading Lab net R are NOT directly interchangeable.',
                         'If a 30-day archive has fewer than 20 preceding full sessions, upstream may refuse the trade.',
                         'Read-only diagnostic; no broker or live trading.']}
    (output/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0 if summary['completed'] else 2

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--history',required=True)
    p.add_argument('--output')
    p.add_argument('--repo')
    p.add_argument('--offline-dir')
    p.add_argument('--limit',type=int,default=3)
    p.add_argument('--target',type=int,choices=(1,2),default=2)
    p.add_argument('--replays',type=int,default=500)
    p.add_argument('--seed',type=int,default=19)
    a=p.parse_args()
    if not (1<=a.limit<=10 and 100<=a.replays<=20000):p.error('limits: 1<=limit<=10 and 100<=replays<=20000')
    try:return audit(a)
    except (RuntimeError,subprocess.TimeoutExpired) as e:
        print(str(e),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
