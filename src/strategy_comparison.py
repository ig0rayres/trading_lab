"""Read-only historical strategy variants. Chronological train/test, never routes orders.

Every variant is evaluated on the SAME session universe, including NO_SIGNAL and
non-executable cases. Validation is not used to pick winners. No broker imports.
"""
import argparse
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from day_replay import fetch_history, replay_day, DEFAULT, NY

VARIANTS={
    'ORB_BASELINE':{},
    'ORB_AFTER_1000':{'earliest':'10:00'},
    'ORB_AFTER_1030':{'earliest':'10:30'},
    'ORB_BREAK_010PCT':{'min_break_pct':0.10},
    'ORB_VOL_150':{'min_rel_volume':1.5},
    'ORB_1000_VOL_150':{'earliest':'10:00','min_rel_volume':1.5},
}

def metrics(rows):
    valid=[r for r in rows if r['status']=='EVALUATED']
    n=len(valid); all_count=len(rows)
    rs=[r['net_r'] for r in valid]; wins=sum(x>0 for x in rs)
    return {'sessions_x_directions':all_count,'evaluated':n,'skipped':all_count-n,
            'wins':wins,'losses':sum(x<0 for x in rs),
            'win_rate':round(wins/n,4) if n else None,
            'mean_net_r':round(sum(rs)/n,4) if n else None,
            'net_r_sum_independent':round(sum(rs),4),
            'min_sample_met':n>=30}

def run(symbols=None, sessions=20, fetch=fetch_history, now_utc=None,output='/app/reports/day/strategy-comparison.json'):
    if os.getenv('LIVE_TRADING_ENABLED','false').lower()!='false':raise ValueError('Live forbidden')
    if not 4<=sessions<=40:raise ValueError('Use 4..40 completed sessions')
    now_utc=now_utc or datetime.now(timezone.utc)
    symbols=list(dict.fromkeys(symbols or DEFAULT.split(',')))
    if not symbols or len(symbols)>25 or any(not (s.isascii() and s.isalnum() and 1<=len(s)<=5) for s in symbols):raise ValueError('Invalid symbols')
    rows=[]; errors=[]; today=now_utc.astimezone(NY).date().isoformat()
    for symbol in symbols:
        try:
            bars=fetch(symbol,now_utc); byday={}
            for bar in bars:
                if bar['day']<today:byday.setdefault(bar['day'],[]).append(bar)
            for day in sorted(byday)[-sessions:]:
                daybars=sorted(byday[day],key=lambda b:b['time'])
                for side in ('LONG','SHORT'):
                    for name,settings in VARIANTS.items():
                        outcome=replay_day(daybars,side,**settings)
                        rows.append({'symbol':symbol,'session':day,'side':side,'variant':name,**outcome})
        except Exception as e:errors.append({'symbol':symbol,'error':type(e).__name__})
    dates=sorted(set(r['session'] for r in rows)); cutoff=max(1,int(len(dates)*0.7)) if dates else 0
    train_days=set(dates[:cutoff]); test_days=set(dates[cutoff:])
    summaries={}
    for side in ('LONG','SHORT'):
        side_summaries={}
        for name in VARIANTS:
            selected=[r for r in rows if r['side']==side and r['variant']==name]
            side_summaries[name]={'train':metrics([r for r in selected if r['session'] in train_days]),
                                  'validation':metrics([r for r in selected if r['session'] in test_days])}
        # Benchmark against baseline: only choose if at least 30 TRAIN evaluated cases; otherwise no winner.
        qualified=[(name,v['train']['mean_net_r']) for name,v in side_summaries.items()
                   if v['train']['min_sample_met'] and v['train']['mean_net_r'] is not None]
        chosen=max(qualified,key=lambda pair:pair[1])[0] if qualified else None
        summaries[side]={'variants':side_summaries,'train_selected_variant':chosen,
                         'validation_of_train_selection':side_summaries[chosen]['validation'] if chosen else None,
                         'status':'EXPLORATORY_ONLY' if chosen else 'INSUFFICIENT_TRAIN_SAMPLE'}
    result={'mode':'LONG_SHORT_VARIANT_COMPARISON_RESEARCH_ONLY','generated_at_utc':now_utc.isoformat(),
            'health':'OK_RESEARCH_ONLY' if not errors and rows else 'PARTIAL_DATA',
            'train_sessions':sorted(train_days),'validation_sessions':sorted(test_days),
            'variants':VARIANTS,'directions':summaries,'candidate_results':rows,'errors':errors,
            'orders_sent':0,'authorized_to_trade':False,
            'limitations':['Train/test split is chronological by exchange session across symbols',
                'A 30 evaluated-case TRAIN minimum gates selection; not proof of a trading edge',
                'Validation is held out from selection but repeated use will overfit',
                'Independent symbol-direction outcomes are NOT a portfolio with concurrent position limits',
                'Yahoo unofficial 5m data (~60d), survivorship and missing sessions possible',
                'Stops and targets use OHLC; stop-first on ambiguous candles; simulated fills and costs',
                'SHORT has no borrow availability, locate, borrow fees or margin modeled',
                'No verified historical catalysts; no actual execution authorized']}
    if output:
        p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
        tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(p)
    return result

def main():
    a=argparse.ArgumentParser();a.add_argument('--sessions',type=int,default=20)
    a.add_argument('--symbols',default=DEFAULT)
    a.add_argument('--output',default='/app/reports/day/strategy-comparison.json')
    args=a.parse_args()
    r=run([x.strip().upper() for x in args.symbols.split(',') if x.strip()],args.sessions,output=args.output)
    print(json.dumps({'health':r['health'],'train_sessions':len(r['train_sessions']),
        'validation_sessions':len(r['validation_sessions']),
        'long_selected':r['directions']['LONG']['train_selected_variant'],
        'short_selected':r['directions']['SHORT']['train_selected_variant'],
        'errors':r['errors'],'orders_sent':0,'output':args.output}))
if __name__=='__main__':main()
