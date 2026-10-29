#!/usr/bin/env python3
"""Standalone exploratory VWAP fade and pair-spread tests on *complete* 5m sessions.

Research hypotheses, not a faithful reproduction of any published strategy.
Uses original Yahoo fetch/parser via history.py and its strict complete-session gate.
No order gateway. Pair PnL is an equal-dollar synthetic long/short, not a portfolio.
"""
import argparse
import csv
import datetime as dt
import json
import math
from pathlib import Path
from statistics import mean, pstdev
import sys
from history import NY, load_original, dates_for, get_chart, session_bars

# One-way fee and slippage per side, each leg. Executed at next bar open.
def net_roundtrip(entry, exit_, side, bps):
    if entry <= 0 or exit_ <= 0: raise ValueError('invalid price')
    gross = side*(exit_/entry-1)
    return gross - 2*bps/10000


def vwap_fade(bars, threshold=.012, bps=10):
    """First qualifying LONG: prior candle >= threshold below live-to-date VWAP,
    then next *completed* candle closes higher. Buy following open; leave at
    VWAP-touch or 15:55 close. Stop at earlier 3-bar low (conservative gaps).
    No intrabar future volume used for the signal.
    """
    running_pv=running_v=0.
    vwaps=[]
    for b in bars:
        v=max(0,int(b['volume']))
        running_pv += (b['high']+b['low']+b['close'])/3*v
        running_v += v
        vwaps.append(running_pv/running_v if running_v else None)
    for i in range(5,len(bars)-2):
        prev=bars[i-1]; cur=bars[i]
        if not vwaps[i-1] or not vwaps[i]: continue
        if prev['close'] >= vwaps[i-1]*(1-threshold):continue
        if cur['close'] <= prev['close']:continue
        e=i+1
        if e >= len(bars)-2:continue
        entry=bars[e]['open']; stop=min(b['low'] for b in bars[i-2:i+1])
        if stop >= entry:continue
        # Exits: candle opens below stop -> gap loss, then stop first, then VWAP.
        for j in range(e,len(bars)-1):
            b=bars[j]
            if b['open']<=stop: ex=b['open'];reason='stop_gap'
            elif b['low']<=stop:ex=stop;reason='stop'
            elif vwaps[j] is not None and b['high']>=vwaps[j]:ex=max(entry,vwaps[j]);reason='vwap_touch'
            else:continue
            break
        else:
            ex=bars[-2]['close'];reason='flat'
        pnl=net_roundtrip(entry,ex,1,bps)
        risk=(entry-stop)/entry
        return {'entry_at':bars[e]['start'].isoformat(),'exit_reason':reason,
                'entry':entry,'exit':ex,'net_pct':round(100*pnl,6),
                'net_r':round(pnl/risk,6),'signal_at':cur['end'].isoformat()}
    return None


def pair_day(prior_a,prior_b,today_a,today_b,lookback=20,z_enter=1.5,bps=10):
    """Signal at PREVIOUS daily close only, based on logarithmic price ratio.
    Equal-dollar pairs at NEXT session open and exit same session near close;
    no short borrow or funding in the cost model, so optimistic for real use.
    This is a spread z-score experiment, NOT cointegration.
    """
    if len(prior_a)<lookback or len(prior_b)<lookback:return None
    a=prior_a[-lookback:];b=prior_b[-lookback:]
    ratios=[math.log(x/y) for x,y in zip(a,b)]
    sigma=pstdev(ratios)
    if sigma<1e-9:return None
    z=(ratios[-1]-mean(ratios))/sigma
    if abs(z)<z_enter:return None
    side_a=-1 if z>0 else 1
    ea,xa=today_a[0]['open'],today_a[-2]['close']
    eb,xb=today_b[0]['open'],today_b[-2]['close']
    # 50% notional per leg, sum of both signed returns.
    net=.5*net_roundtrip(ea,xa,side_a,bps)+.5*net_roundtrip(eb,xb,-side_a,bps)
    return {'z_prior_close':round(z,6),'side_a':'short' if side_a<0 else 'long',
            'entry_at':today_a[0]['start'].isoformat(),'exit_reason':'flat',
            'net_pct':round(net*100,6)}


def summarize(rows):
    if not rows:return {'n':0,'mean_net_pct':None,'win_rate_pct':None,'profit_factor':None,'distinct_days':0}
    vals=[float(r['net_pct']) for r in rows]
    gains=sum(v for v in vals if v>0);losses=-sum(v for v in vals if v<0)
    return {'n':len(rows),'mean_net_pct':round(mean(vals),6),'win_rate_pct':round(100*sum(v>0 for v in vals)/len(vals),2),
            'profit_factor':round(gains/losses,4) if losses else None,
            'distinct_days':len({r['date'] for r in rows})}


def main(argv=None):
    p=argparse.ArgumentParser(description='Research-only VWAP and pair hypotheses; not published strategy replication')
    p.add_argument('--days',type=int,default=55);p.add_argument('--from',dest='from_date');p.add_argument('--to',dest='to_date')
    p.add_argument('--symbols',default='AAPL,MSFT,NVDA,AMD,TSLA,META,AMZN,GOOGL')
    p.add_argument('--pairs',default='');p.add_argument('--offline-dir');p.add_argument('--output',default='/app/reports/external/v10')
    p.add_argument('--repo');p.add_argument('--pause',type=float,default=.3)
    p.add_argument('--fee-bps',type=float,default=5);p.add_argument('--slippage-bps',type=float,default=5)
    p.add_argument('--vwap-threshold',type=float,default=.012);p.add_argument('--pair-lookback',type=int,default=20)
    p.add_argument('--pair-z',type=float,default=1.5)
    a=p.parse_args(argv)
    if a.days<1 or min(a.fee_bps,a.slippage_bps,a.pause)<0 or not 0<a.vwap_threshold<.5 or a.pair_lookback<5 or a.pair_z<=0:p.error('invalid configuration')
    try:
        pairs=[]
        for item in a.pairs.split(','):
            if item.strip():
                parts=[x.strip().upper() for x in item.split(':')]
                if len(parts)!=2 or parts[0]==parts[1] or any(not x.isalnum() for x in parts):raise ValueError('pairs format AAPL:MSFT,NVDA:AMD')
                pairs.append(parts)
        symbols=list(dict.fromkeys([x.strip().upper() for x in a.symbols.split(',') if x.strip()]+[s for pair in pairs for s in pair]))
        if not symbols or len(symbols)>30 or any(not s.isalnum() or len(s)>12 for s in symbols):raise ValueError('invalid symbols; maximum 30')
        original=load_original(a.repo)
        today=dt.datetime.now(NY).date()
        dates=dates_for(a,today,original)
    except (ValueError,RuntimeError) as exc:p.error(str(exc))
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    data={};diagnostics=[];vrows=[];prows=[]
    bp=a.fee_bps+a.slippage_bps
    for sym in symbols:
        try:
            chart=get_chart(original,sym,dates,today,out/'cache',a.offline_dir,a.pause)
            days={}
            for day in dates:
                bars,err=session_bars(original,chart,day)
                if err:diagnostics.append({'symbol':sym,'date':str(day),'reason':err})
                else:
                    days[day]=bars
                    trade=vwap_fade(bars,a.vwap_threshold,bp)
                    if trade:vrows.append({'strategy':'vwap_fade','symbol':sym,'date':str(day),**trade})
            data[sym]=days
        except Exception as exc:diagnostics.append({'symbol':sym,'reason':'FETCH_OR_PARSE:'+str(exc)})
    for sa,sb in pairs:
        da=data.get(sa,{});db=data.get(sb,{})
        shared=sorted(set(da)&set(db))
        for day in shared:
            prev=[d for d in shared if d<day]
            prior_a=[da[d][-1]['close'] for d in prev];prior_b=[db[d][-1]['close'] for d in prev]
            result=pair_day(prior_a,prior_b,da[day],db[day],a.pair_lookback,a.pair_z,bp)
            if result:prows.append({'strategy':'pair_ratio_z','symbol':sa+':'+sb,'date':str(day),**result})
    for name,rows in [('vwap_trades.csv',vrows),('pair_trades.csv',prows)]:
        keys=list(dict.fromkeys(k for row in rows for k in row)) or ['strategy','symbol','date','net_pct']
        with (out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
    (out/'diagnostics.json').write_text(json.dumps(diagnostics,indent=2))
    summary={'status':'EXPLORATORY_HYPOTHESES_NOT_REPRODUCED_PUBLICATION_OR_LIVE_APPROVED',
             'date_start':str(dates[0]),'date_end':str(dates[-1]),'symbols':symbols,'pairs':pairs,
             'vwap':summarize(vrows),'pair_ratio_z':summarize(prows),'diagnostics':len(diagnostics),
             'parameters':{'vwap_threshold':a.vwap_threshold,'pair_lookback':a.pair_lookback,
                           'pair_z':a.pair_z,'fees_bps_per_side':a.fee_bps,'slippage_bps_per_side':a.slippage_bps},
             'warnings':['These are NEW hypotheses, NOT verified reproductions of published studies.',
                         'Pairs use price ratio z-score, NOT cointegration tests.',
                         'Pairs assume short selling with no locate/borrow fees and can be optimistic.',
                         'Each signal isolated; no portfolio, market impact or simultaneous exposure.',
                         'Existing data feed limited to roughly 60 calendar days and potentially biased universe.',
                         'No independent untouched holdout; no live orders; no approved trading strategy.']}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2));return 0
if __name__=='__main__':sys.exit(main())
