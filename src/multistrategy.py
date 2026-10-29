#!/usr/bin/env python3
"""Research-only multi-strategy driver; upstream entry and exit rules are authoritative.

No execution gateway. Signals from bars as of each date only. Daily-price level
strategies require complete sessions *before* the evaluation date. Data is
subject to Yahoo's ~60-day 5m limitation and modern-universe bias.
"""
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import sys

from history import (NY, load_original, dates_for, parse_symbol_list, get_chart,
                     session_bars, simulate_day, metrics)

STRATEGIES = {
    'orb_15_mid': {'setup':'orb','stop_rule':'or-mid'},
    'orb_15_low': {'setup':'orb','stop_rule':'or-low'},
    'orb_15_volume15': {'setup':'orb','stop_rule':'or-mid','min_volume_x':1.5},
    'prev_high_breakout': {'setup':'level','stop_rule':'pct:1','lookback':1},
    'high20_breakout': {'setup':'level','stop_rule':'pct:1','lookback':20},
    'bull_flag_breakout': {'setup':'level','stop_rule':'pct:1','lookback':1,'scanner_tag':'bull_flag'},
    'ma20_reclaim_breakout': {'setup':'level','stop_rule':'pct:1','lookback':1,'scanner_tag':'reclaim_ma20'},
    'oversold_bounce_breakout': {'setup':'level','stop_rule':'pct:1','lookback':1,'scanner_tag':'oversold_bounce'},
}


def previous_level(completed, date, n):
    """Highest HIGH of n preceding full sessions; never inspect current day."""
    earlier=[(day,bars) for day,bars in completed.items() if day<date]
    earlier.sort(key=lambda pair:pair[0])
    if len(earlier)<n:return None
    return max(float(b['high']) for _,bars in earlier[-n:] for b in bars)


def scanner_tags_prior(orig, completed, date):
    """Run original daily scanner rules using prior fully completed sessions ONLY."""
    prior=sorted((d,b) for d,b in completed.items() if d<date)
    closes=[float(b[-1]['close']) for _,b in prior]
    if len(closes)<30:return set()
    tags,_=orig.scanner.find_setups(closes)
    return set(tags)


def variants(orig, chart, bars, date, completed, strategies, targets, fees, slip, budget):
    results=[]; skips=[]
    prior_tags=scanner_tags_prior(orig,completed,date) if any(STRATEGIES[x].get('scanner_tag') for x in strategies) else set()
    for name in strategies:
        cfg=STRATEGIES[name]
        if cfg.get('scanner_tag') and cfg['scanner_tag'] not in prior_tags:
            continue
        level=None
        if cfg.get('lookback'):
            level=previous_level(completed,date,cfg['lookback'])
            if level is None:
                skips.append({'symbol':chart['symbol'],'date':date.isoformat(),'strategy':name,'reason':'INSUFFICIENT_PAST_COMPLETE_SESSIONS'})
                continue
        for target in targets:
            try:
                row=simulate_day(orig,chart,bars,date,target,fees,slip,budget,
                                 cfg['stop_rule'],setup=cfg['setup'],level=level,
                                 min_volume_x=cfg.get('min_volume_x'))
                if row:
                    row['strategy']=name
                    row['level_from_past']=round(level,6) if level else ''
                    results.append(row)
            except Exception as exc:
                skips.append({'symbol':chart['symbol'],'date':date.isoformat(),
                              'strategy':name,'target_r':target,'reason':'REPLAY:'+str(exc)})
    return results,skips


def main(argv=None):
    p=argparse.ArgumentParser(description='Multi-strategy historical research, upstream modules, no broker')
    p.add_argument('--days',type=int,default=55)
    p.add_argument('--from',dest='from_date');p.add_argument('--to',dest='to_date')
    p.add_argument('--symbols',default='TSLA,NVDA,AMD')
    p.add_argument('--symbols-file');p.add_argument('--max-symbols',type=int,default=30)
    p.add_argument('--strategies',default=','.join(STRATEGIES))
    p.add_argument('--targets',default='1,2')
    p.add_argument('--offline-dir');p.add_argument('--output',default='/app/reports/multistrategy/v08')
    p.add_argument('--repo');p.add_argument('--fee-bps',type=float,default=5)
    p.add_argument('--slippage-bps',type=float,default=5);p.add_argument('--budget-usd',type=float,default=5000)
    p.add_argument('--pause',type=float,default=.3);p.add_argument('--refresh',action='store_true')
    a=p.parse_args(argv)
    try:
        names=[s.strip() for s in a.strategies.split(',') if s.strip()]
        if not names or any(s not in STRATEGIES for s in names):raise ValueError('Invalid strategy; choices: '+','.join(STRATEGIES))
        targets=[float(x) for x in a.targets.split(',')]
        if not targets or any(x<=0 for x in targets):raise ValueError('Targets must be > 0')
        if a.days<1 or a.budget_usd<=0 or min(a.fee_bps,a.slippage_bps,a.pause)<0:raise ValueError('Invalid days/budget/costs')
        orig=load_original(a.repo)
        today=dt.datetime.now(NY).date()
        dates=dates_for(a,today,orig)
        symbols=parse_symbol_list(a)
    except (ValueError,RuntimeError) as exc:p.error(str(exc))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    all_rows=[];errors=[];complete_count=0
    for ix,sym in enumerate(symbols,1):
        try:
            chart=get_chart(orig,sym,dates,today,out/'cache',a.offline_dir,a.pause,a.refresh)
        except Exception as exc:
            errors.append({'symbol':sym,'reason':'FETCH:'+str(exc)})
            print('Processed %d/%d (fetch failure)'%(ix,len(symbols)),flush=True)
            continue
        complete={}
        for day in dates:
            bars,err=session_bars(orig,chart,day)
            if err:errors.append({'symbol':sym,'date':day.isoformat(),'reason':err})
            else:complete[day]=bars
        complete_count+=len(complete)
        for day in sorted(complete):
            rows,failed=variants(orig,chart,complete[day],day,complete,names,targets,a.fee_bps,a.slippage_bps,a.budget_usd)
            all_rows.extend(rows);errors.extend(failed)
        print('Processed %d/%d symbols'%(ix,len(symbols)),flush=True)
    fields=['strategy','level_from_past','symbol','date','signal_at','entry_at','or_high','or_low','entry_raw','entry_fill','stop','target','target_r','exit_at','exit_reason','exit_fill','pnl_per_share','net_r','net_pct','budget_qty','risk_verdict','risk_reasons','upstream_commit']
    with (out/'trades.csv').open('w',newline='',encoding='utf-8') as fh:
        wr=csv.DictWriter(fh,fieldnames=fields,extrasaction='ignore');wr.writeheader();wr.writerows(all_rows)
    (out/'errors.json').write_text(json.dumps(errors,indent=2))
    cut=dates[max(0,int(len(dates)*.7)-1)]
    report={}
    for name in names:
        report[name]={}
        for target in targets:
            subset=[x for x in all_rows if x['strategy']==name and x['target_r']==target]
            report[name][str(target)+'R']={'all':metrics(subset),
              'earlier_sessions':metrics([x for x in subset if x['date']<=cut.isoformat()]),
              'later_sessions':metrics([x for x in subset if x['date']>cut.isoformat()])}
    summary={'status':'MULTISTRATEGY_EXPLORATORY_NOT_VALIDATED','upstream_commit':orig.commit,
      'strategies':report,'strategy_definitions':{n:STRATEGIES[n] for n in names},
      'start':dates[0].isoformat(),'end':dates[-1].isoformat(),'dates_requested':len(dates),
      'complete_symbol_sessions':complete_count,'symbols':symbols,'total_evaluations':len(all_rows),
      'diagnostics':len(errors),'assumptions':{'exit_at':'5 min before exchange close',
      'ambiguous_bar':'stop first','fee_bps_per_side':a.fee_bps,'slippage_bps_per_side':a.slippage_bps},
      'warnings':['Research only; independent per-share hypotheticals, not portfolio PnL.',
      'Repeated strategy/target evaluations are correlated, not independent trades.',
      'Previous-level variants use highs from fully completed earlier sessions only.',
      'Zero evaluations may mean insufficient lookback, absent trigger, or errors; inspect errors.json.',
      'Yahoo 5m limited and unofficial; present-day ticker universe causes selection bias.',
      'Chronological splits are descriptive only; no untouched holdout or edge established.',
      'No broker connection; never authorize real orders based on this report.']}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2));print('Report:',out)
    return 0 if all_rows else 2

if __name__=='__main__':sys.exit(main())
