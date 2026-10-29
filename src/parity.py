#!/usr/bin/env python3
"""Offline diagnostic: compare v0.5 signal/stop/target with original modules.

Never changes prior CSV; no market HTTP and no broker calls. A difference in
slippage or rounding is documented, not automatically resolved.
"""
import argparse
import csv
import datetime as dt
from decimal import Decimal
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo
from original import load_original
from history import parse_strict_chart

NY=ZoneInfo('America/New_York')


def check_one(orig, day, hit, per_target, cached):
    sym=hit['symbol']
    chart=parse_strict_chart(orig,cached.read_text(encoding='utf-8'),sym)
    clock=dt.datetime.combine(day,orig.entry.session(day)[1],NY).astimezone(dt.timezone.utc).replace(tzinfo=None)
    res=orig.entry.evaluate(chart,clock,setup='orb',or_minutes=15,interval='5m')
    original_time=(res.get('trigger') or {}).get('time') if res['status']=='triggered' else None
    expected=hit.get('at')
    ret={'symbol':sym,'scanner_time':expected,'original_entry_time':original_time,
         'entry_match':original_time==expected,'price_match':False,'stop_match':False,
         'target_match':False,'differences':[]}
    if original_time!=expected:ret['differences'].append('ENTRY_SIGNAL_MISMATCH')
    if original_time and abs(float(res['trigger']['price'])-float(hit['price']))<=.011:
        ret['price_match']=True
    else:
        ret['differences'].append('PRICE_MISMATCH')
    # Compare original exit rules using the SAME approximate already-slipped
    # v0.5 fill, not a different hypothetical order fill.
    ok_stop=ok_target=True
    for k in (1,2):
        old=per_target.get(k)
        if old is None:
            ret['differences'].append('NO_V05_TRADE_%dR'%k);ok_stop=ok_target=False;continue
        p=orig.exit.compute(old['entry_fill'],'or_mid',None,'r',Decimal(k),
                            or_high=hit['or_high'],or_low=hit['or_low'])
        sd=abs(Decimal(str(p['stop']))-Decimal(str(old['stop'])))
        td=abs(Decimal(str(p['target']))-Decimal(str(old['target'])))
        if sd>Decimal('0.0001'):
            ok_stop=False;ret['differences'].append('STOP_%dR_DELTA_%s'%(k,sd))
        if td>Decimal('0.0001'):
            ok_target=False;ret['differences'].append('TARGET_%dR_DELTA_%s'%(k,td))
    ret['stop_match']=ok_stop;ret['target_match']=ok_target
    return ret


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--date',default='2026-10-26')
    ap.add_argument('--limit',type=int,default=0)
    ap.add_argument('--watchlist',help='Default: /app/reports/orb/watchlist-DATE.json')
    ap.add_argument('--trades',help='Existing intraday or final v0.5 trades.csv')
    ap.add_argument('--cache',help='Raw Yahoo JSON cache from v0.5')
    ap.add_argument('--repo',help='Original upstream repo')
    ap.add_argument('--output',help='Default: /app/reports/parity/DATE/summary.json')
    a=ap.parse_args(argv)
    orig=load_original(a.repo)
    day=dt.date.fromisoformat(a.date)
    root=Path('/app/reports/orb')
    watchfile=Path(a.watchlist or root/('watchlist-%s.json'%day))
    resultfolder=root/('batch-%s'%day)
    intraday=root/('intraday-%s'%day)
    csvfile=Path(a.trades or (intraday/'trades.csv' if (intraday/'trades.csv').is_file() else resultfolder/'trades.csv'))
    cache_dir=Path(a.cache or (csvfile.parent/'cache'))
    out=Path(a.output or ('/app/reports/parity/%s/summary.json'%day))
    hits=json.loads(watchfile.read_text())['hits']
    if a.limit>0:hits=hits[:a.limit]
    with csvfile.open(newline='') as f:prev=list(csv.DictReader(f))
    v05={}
    for row in prev:
        if row['date']==a.date:
            v05.setdefault(row['symbol'],{})[int(float(row['target_r']))]=row
    rows=[]
    for h in hits:
        sym=h['symbol']
        cache_file=cache_dir/(sym.replace('/','_')+'.json')
        if not cache_file.exists():
            rows.append({'symbol':sym,'entry_match':False,'target_match':False,'stop_match':False,
                         'differences':['MISSING_V05_RAW_CACHE']});continue
        try:rows.append(check_one(orig,day,h,v05.get(sym,{}),cache_file))
        except Exception as exc:
            rows.append({'symbol':sym,'entry_match':False,'target_match':False,'stop_match':False,
                         'differences':['ERROR:'+str(exc)]})
    summary={'status':'DIAGNOSTIC_PARITY_NOT_TRADING','upstream_commit':orig.commit,
        'date':a.date,'signals':len(rows),
        'entry_match':sum(r.get('entry_match') is True for r in rows),
        'stop_match':sum(r.get('stop_match') is True for r in rows),
        'target_match':sum(r.get('target_match') is True for r in rows),
        'mismatches':[r for r in rows if r.get('differences')],
        'note':'v0.5 and original may differ due cent rounding/slippage; nothing silently reconciled.'}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps({k:(v if k!='mismatches' else v[:10]) for k,v in summary.items()},indent=2))
    print('Full parity report:',out)
    return 0 if summary['entry_match']==len(rows) and summary['stop_match']==len(rows) and summary['target_match']==len(rows) else 2

if __name__=='__main__':sys.exit(main())
