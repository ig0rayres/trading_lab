#!/usr/bin/env python3
"""Minimal multi-market research lab. No broker, no live trading, stdlib only.
CSV: timestamp,open,high,low,close,volume,session (session=YYYY-MM-DD exchange-local).
Bars in chronological order; timestamps ISO 8601; timestamps should have timezone offsets.
Signals use fully closed bar i and enter at next bar open. Never trades across sessions.
"""
import argparse,csv,datetime as dt,json,math,statistics
from pathlib import Path

def read_bars(path):
    bars=[]
    with open(path,newline='') as f:
        for row in csv.DictReader(f):
            b={k:float(row[k]) for k in ('open','high','low','close','volume')}
            b.update(timestamp=row['timestamp'],session=row['session'])
            if not (0<b['low']<=min(b['open'],b['close'])<=max(b['open'],b['close'])<=b['high'] and b['volume']>=0):
                raise ValueError('invalid OHLCV: '+str(row))
            bars.append(b)
    if any(bars[i]['timestamp']>=bars[i+1]['timestamp'] for i in range(len(bars)-1)):
        raise ValueError('bars are not strictly sorted')
    return bars

def signal(strategy,session,i):
    """Signal at a closed bar. No forward information."""
    if i<5:return False
    closes=[b['close'] for b in session[:i+1]]
    if strategy=='orb':
        return i>=5 and closes[i]>max(b['high'] for b in session[:3]) and closes[i-1]<=max(b['high'] for b in session[:3])
    if strategy=='momentum':
        vols=[b['volume'] for b in session[i-5:i]]
        return closes[i]>max(closes[i-5:i]) and session[i]['volume']>1.5*statistics.mean(vols)
    if strategy=='vwap':
        def vwap(j):
            bs=session[:j+1]; den=sum(x['volume'] for x in bs)
            return sum(((x['high']+x['low']+x['close'])/3)*x['volume'] for x in bs)/den if den else float('nan')
        return closes[i]>vwap(i) and closes[i-1]<=vwap(i-1)
    raise ValueError(strategy)

def simulate(bars,strategy,fee_bps=5,slippage_bps=5,stop_pct=.0075,target_r=1.5):
    sessions={}
    for b in bars:sessions.setdefault(b['session'],[]).append(b)
    trades=[]
    for day,ss in sorted(sessions.items()):
        if len(ss)<12:continue
        # one entry per session, entry at NEXT bar open, exit at stop/target or final close
        for i in range(5,len(ss)-2):
            if not signal(strategy,ss,i):continue
            entry=ss[i+1]['open']*(1+slippage_bps/10000)
            stop=entry*(1-stop_pct); target=entry*(1+stop_pct*target_r)
            out=None;exit_at=None
            for j in range(i+1,len(ss)):
                b=ss[j]
                if j==i+1 and b['open']<=stop:out=b['open'];exit_at=j;break
                if b['low']<=stop:out=min(stop,b['open']);exit_at=j;break # stop first if both hit
                if b['high']>=target:out=target;exit_at=j;break
            if out is None:out=ss[-1]['close'];exit_at=len(ss)-1
            exit_price=out*(1-slippage_bps/10000)
            net_pct=(exit_price-entry)/entry-(2*fee_bps/10000)
            trades.append({'session':day,'strategy':strategy,'signal':ss[i]['timestamp'],'entry':entry,'exit':exit_price,'net_pct':net_pct*100,'r':net_pct/stop_pct,'exit_time':ss[exit_at]['timestamp']})
            break
    return trades

def report(trades):
    if not trades:return {'n':0,'status':'INSUFFICIENT_DATA'}
    returns=[t['net_pct'] for t in trades];wins=sum(r>0 for r in returns)
    pos=sum(max(0,r) for r in returns);neg=-sum(min(0,r) for r in returns)
    equity=peak=1.;maxdd=0
    for r in returns:
        equity*=1+r/100;peak=max(peak,equity);maxdd=max(maxdd,1-equity/peak)
    return {'n':len(trades),'win_rate_pct':round(100*wins/len(trades),2),'mean_net_pct':round(statistics.mean(returns),4),'profit_factor':round(pos/neg,3) if neg else None,'max_drawdown_pct':round(100*maxdd,3),'total_net_pct_compounded':round((equity-1)*100,3)}

def run(path,output,fees,slippage):
    bars=read_bars(path)
    dates=sorted(set(b['session'] for b in bars));cut=int(len(dates)*.7)
    train=set(dates[:cut]);test=set(dates[cut:]);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    result={'disclaimer':'Research only. No brokerage integration. CSV data quality and costs must be validated before financial conclusions.', 'source':str(path),'sessions':len(dates),'train_sessions':len(train),'test_sessions':len(test),'cost_assumptions':{'fee_bps_per_side':fees,'slippage_bps_per_side':slippage},'strategies':{}}
    for strat in ('orb','vwap','momentum'):
        a=simulate([b for b in bars if b['session'] in train],strat,fees,slippage)
        b=simulate([b for b in bars if b['session'] in test],strat,fees,slippage)
        stressed=simulate([x for x in bars if x['session'] in test],strat,fees*2,slippage*2)
        result['strategies'][strat]={'train':report(a),'test':report(b),'test_costs_x2':report(stressed),'decision':'INSUFFICIENT_EVIDENCE' if len(b)<100 else ('RESEARCH_CANDIDATE' if report(b)['mean_net_pct']>0 and report(stressed)['mean_net_pct']>0 else 'REJECT')}
        with open(output/(strat+'_trades.csv'),'w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['session','strategy','signal','entry','exit','net_pct','r','exit_time']);w.writeheader();w.writerows(a+b)
    (output/'report.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--output',default='reports');p.add_argument('--fee-bps',type=float,default=5);p.add_argument('--slippage-bps',type=float,default=5);a=p.parse_args();run(a.csv,a.output,a.fee_bps,a.slippage_bps)
