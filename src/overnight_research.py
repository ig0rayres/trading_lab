#!/usr/bin/env python3
"""Exploratory reproduction of paper's overnight/daytime rules, not its WRDS data.
Positions: (overnight,daytime). Signals only from periods already completed.
Every change in signed exposure incurs one-way transaction cost by position delta.
No margin/borrow or market impact; results with shorts are optimistic.
"""
import argparse,csv,datetime as dt,json,math
from pathlib import Path
from candidate_research import yahoo_daily

ETFS=['SPY','XLB','XLE','XLF','XLI','XLK','XLP','XLU','XLV','XLY']
STRATEGIES=['long_cash','cash_long','cash_reversal','reversal_cash','long_reversal','long_long']

def positions(name,previous_day,overnight):
    sign=lambda x: 1 if x>=0 else -1
    return {
      'long_cash':(1,0),'cash_long':(0,1),
      'cash_reversal':(0,-sign(overnight)),
      'reversal_cash':(-sign(previous_day),0),
      'long_reversal':(1,-sign(overnight)),
      'long_long':(1,1),
    }[name]

def simulation(rows,name,cost_bps):
    """Ordered adjusted open/close; decide night after previous close and day at current open."""
    rows=sorted(rows,key=lambda x:x['date']);out=[];equity=1.;pos=0
    if len(rows)<3:return out
    for i in range(2,len(rows)):
        past=rows[i-1];prevprev=rows[i-2];cur=rows[i]
        past_day=past['close']/past['open']-1
        night=cur['open']/past['close']-1
        day=cur['close']/cur['open']-1
        pn,pd=positions(name,past_day,night)
        change=abs(pn-pos)+abs(pd-pn)
        gross=(1+pn*night)*(1+pd*day)-1
        # Position transitions are modeled on separate fill events.
        pnl=gross-change*cost_bps/10000
        equity*=max(0.,1+pnl)
        out.append({'date':cur['date'],'net_return':pnl,'equity':equity,'turnover':change,'overnight_position':pn,'day_position':pd})
        pos=pd
    # Charge final close-out if still exposed; not an additional signal.
    if out and pos:
        fee=abs(pos)*cost_bps/10000
        out[-1]['net_return']-=fee
        equity*=1-fee
        out[-1]['equity']=equity
        out[-1]['turnover']+=abs(pos)
    return out

def stats(rows):
    if not rows:return {'n':0,'total_return_pct':None,'annualized_pct':None,'max_drawdown_pct':None,'turnover':0}
    eq=1.;peak=1.;dd=0.
    for r in rows:
        eq*=max(0,1+r['net_return']);peak=max(peak,eq);dd=min(dd,eq/peak-1)
    return {'n':len(rows),'total_return_pct':round((eq-1)*100,4),'annualized_pct':round((eq**(252/len(rows))-1)*100,4) if eq else -100.,'max_drawdown_pct':round(100*dd,4),'turnover':round(sum(r['turnover'] for r in rows),2)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--cache-dir',default='/app/reports/candidates/v12/cache')
    p.add_argument('--from',dest='start',default='2021-01-01');p.add_argument('--to',dest='end',default='2026-10-23')
    p.add_argument('--split',default='2025-01-01');p.add_argument('--symbols',default=','.join(ETFS))
    p.add_argument('--cost-bps',default='2,5,10');p.add_argument('--output',default='/app/reports/overnight/v13')
    args=p.parse_args()
    if not args.start<args.split<=args.end:p.error('invalid date/split')
    costs=[float(x) for x in args.cost_bps.split(',')]
    if not costs or any(not math.isfinite(c) or c<0 for c in costs):p.error('invalid costs')
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    cache=Path(args.cache_dir);results={};errors={};saved=[]
    for symbol in dict.fromkeys(x.strip().upper() for x in args.symbols.split(',') if x.strip()):
        # Reuse existing locally cached Yahoo JSON, never fetch if not supplied.
        matches=sorted(cache.glob(symbol+'_*.json'))
        if not matches:
            errors[symbol]='MISSING_CACHED_DAILY_DATA';continue
        try:
            # Reparse adjusted series through the existing reusable function.
            filename=matches[-1].name
            stem=filename[len(symbol)+1:-5]
            st,en=stem.split('_')
            data=yahoo_daily(symbol,st,en,cache)
            rows=[data[d] for d in sorted(data) if args.start<=d<=args.end]
            if len(rows)<50:errors[symbol]='INSUFFICIENT_SESSIONS';continue
            results[symbol]={}
            for name in STRATEGIES:
                results[symbol][name]={}
                for cost in costs:
                    trades=simulation(rows,name,cost)
                    a=[r for r in trades if r['date']<args.split]
                    b=[r for r in trades if r['date']>=args.split]
                    results[symbol][name][str(cost)]={'all':stats(trades),'development':stats(a),'validation':stats(b)}
                    for r in trades:saved.append((symbol,name,cost,r))
        except Exception as exc:errors[symbol]='PARSE_FAILURE: '+str(exc)[:150]
    with (output/'daily_returns.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['symbol','strategy','cost_bps','date','net_return','equity','turnover','overnight_position','day_position'])
        for s,n,c,r in saved:w.writerow([s,n,c,r['date'],r['net_return'],r['equity'],r['turnover'],r['overnight_position'],r['day_position']])
    report={'status':'EXPLORATORY_PAPER_RULES_NOT_WRDS_REPRODUCTION_OR_LIVE_APPROVAL','reference':'Salotra et al., Risks 2026, DOI 10.3390/risks14040084','period':{'start':args.start,'end':args.end,'split':args.split},'cost_bps_one_way_per_position_change':costs,'strategies':results,'errors':errors,'warnings':['Same paper rule definitions but different shorter Yahoo sample and simplified linear execution costs.','Adjusted OHLC derived from Yahoo close adjustment; verify corporate actions and open prices.','Daily open/close execution at printed prices is optimistic, especially for close auction.','Short strategies ignore borrow availability, borrow fees, margin and financing.','Period 2025-2026 is already known; not untouched holdout.','No portfolio accounting or real orders.']}
    (output/'summary.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'status':report['status'],'strategies':STRATEGIES,'symbols':list(results),'errors':errors,'output':str(output),'records':len(saved)},indent=2))

if __name__=='__main__':main()
