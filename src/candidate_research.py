#!/usr/bin/env python3
"""Research-only daily screening of four adapted hypotheses, fifth requires intraday archive.
No strategy is a faithful reproduction of an academic portfolio. No broker, no orders.
Uses completed daily adjusted Yahoo OHLC, close-to-close decisions with one-session lag.
"""
import argparse, csv, datetime as dt, json, math, statistics, time, urllib.request
from pathlib import Path

DEFAULT='SPY,QQQ,IWM,GLD,TLT,AAPL,MSFT,NVDA,AMD,AMZN,META,GOOGL'

def yahoo_daily(symbol,start,end,cache):
    cache.mkdir(parents=True,exist_ok=True)
    target=cache/f'{symbol}_{start}_{end}.json'
    if target.exists(): data=json.loads(target.read_text())
    else:
        a=int(dt.datetime.combine(dt.date.fromisoformat(start),dt.time(),dt.timezone.utc).timestamp())
        b=int(dt.datetime.combine(dt.date.fromisoformat(end)+dt.timedelta(days=1),dt.time(),dt.timezone.utc).timestamp())
        u=f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={a}&period2={b}&interval=1d&events=div%2Csplits'
        req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 TradingLab-Research/1.2'})
        with urllib.request.urlopen(req,timeout=35) as response:data=json.load(response)
        target.write_text(json.dumps(data))
    result=data['chart']['result'][0]; q=result['indicators']['quote'][0]
    adj=result['indicators'].get('adjclose',[{}])[0].get('adjclose',q['close'])
    rows=[]
    for i,t in enumerate(result['timestamp']):
        c=q['close'][i]; o=q['open'][i]; a=adj[i] if i<len(adj) else None
        if not c or not o or not a or min(o,c,a)<=0:continue
        date=dt.datetime.fromtimestamp(t,dt.timezone.utc).date().isoformat()
        rows.append({'date':date,'open':o*a/c,'close':a})
    return {r['date']:r for r in rows}

def csv_daily(symbol,path):
    f=Path(path)/f'{symbol}.csv'
    with f.open(newline='') as h: data=list(csv.DictReader(h))
    if not {'date','open','close'}.issubset(data[0] if data else {}):raise ValueError(f'{f} requires date,open,close (adjusted prices)')
    return {r['date']:{'date':r['date'],'open':float(r['open']),'close':float(r['close'])} for r in data if float(r['open'])>0 and float(r['close'])>0}

def nav_returns(prices, decisions, cost_bps=10):
    """Decision after close i; hold on close i to close i+1; change positions at next open proxy.
    Price series based on total-return adjusted close. Trading costs on absolute weight turnover.
    Daily portfolios marked at adjusted closes; signals lagged, no future-bar selection.
    """
    dates=sorted(prices); equity=1.; prev={}; daily=[]
    for i in range(len(dates)-1):
        d,nd=dates[i],dates[i+1]; weights=decisions(d,i,dates,prices)
        weights={k:v for k,v in weights.items() if k in prices[d] and k in prices[nd] and abs(v)>1e-12}
        turnover=sum(abs(weights.get(k,0)-prev.get(k,0)) for k in set(prev)|set(weights))
        pnl=sum(w*(prices[nd][s]/prices[d][s]-1) for s,w in weights.items())-turnover*cost_bps/10000
        equity*=max(0,1+pnl)
        daily.append({'date':nd,'net_return':pnl,'equity':equity,'turnover':turnover})
        prev=weights
    if daily and prev:
        fee=sum(abs(v) for v in prev.values())*cost_bps/10000
        equity*=max(0,1-fee);daily[-1]['net_return']-=fee;daily[-1]['equity']=equity
    return daily

def summarize(rows,split='2025-01-01'):
    def part(data):
        if not data:return {'days':0,'total_return_pct':None,'annualized_pct':None,'max_drawdown_pct':None,'positive_days_pct':None}
        eq=1.;peak=1.;draw=0.
        for x in data:
            eq*=max(0,1+x['net_return']);peak=max(peak,eq);draw=min(draw,eq/peak-1)
        return {'days':len(data),'total_return_pct':round(100*(eq-1),4),'annualized_pct':round(100*(eq**(252/len(data))-1),4) if eq>0 else -100,'max_drawdown_pct':round(100*draw,4),'positive_days_pct':round(100*sum(x['net_return']>0 for x in data)/len(data),2)}
    return {'all':part(rows),'development':part([r for r in rows if r['date']<split]),'validation':part([r for r in rows if r['date']>=split])}

def build(prices, start, end, fee):
    dates=sorted(prices)
    def prevmonth(i):return i>0 and dates[i][:7]!=dates[i-1][:7]
    def tsmom(d,i,ds,p):
        if i<252:return {}
        basket=['SPY','QQQ','IWM','GLD','TLT'];available=[s for s in basket if s in p[d] and s in p[ds[i-252]]]
        selected=[s for s in available if p[d][s]>p[ds[i-252]][s]]
        return {s:1/len(available) for s in selected} if available else {}
    def high52(d,i,ds,p):
        if i<252:return {}
        candidates=['AAPL','MSFT','NVDA','AMD','AMZN','META','GOOGL']
        scores=[]
        for s in candidates:
            h=[p[ds[j]][s] for j in range(i-251,i+1) if s in p[ds[j]]]
            if len(h)>=240:scores.append((p[d][s]/max(h),s))
        top=sorted(scores,reverse=True)[:2]
        return {s:1/len(top) for _,s in top} if top else {}
    def tom(d,i,ds,p):
        if 'SPY' not in p[d]:return {}
        # Last session + first three sessions of month; next-day position decided at previous close.
        nxt=ds[i+1] if i+1<len(ds) else d
        end_month=nxt[:7]!=d[:7]
        first_three=sum(z[:7]==d[:7] for z in ds[:i+1])<=3
        return {'SPY':1} if first_three or end_month else {}
    # Pairs screening: after close, find relative divergence in normalized trailing 60-session prices.
    # Not Gatev reproduction: ratios, fixed named pairs, no 12-month formation / 6-month trading.
    def pairs(d,i,ds,p):
        if i<61:return {}
        selected=[]
        for a,b in [('AAPL','MSFT'),('NVDA','AMD')]:
            hist=[(p[ds[j]][a],p[ds[j]][b]) for j in range(i-60,i+1) if a in p[ds[j]] and b in p[ds[j]]]
            if len(hist)!=61:continue
            ratios=[math.log(x/y) for x,y in hist[:-1]]
            sigma=statistics.pstdev(ratios)
            if sigma<=1e-8:continue
            z=(math.log(hist[-1][0]/hist[-1][1])-statistics.mean(ratios))/sigma
            if abs(z)>2:selected.append((a,b,-1 if z>0 else 1))
        if not selected:return {}
        weights={}
        for a,b,side in selected:
            weights[a]=weights.get(a,0)+side*.5/len(selected)
            weights[b]=weights.get(b,0)-side*.5/len(selected)
        return weights
    methods={'tsmom_etf_long_cash':tsmom,'high52_long_top2':high52,'turn_of_month_spy':tom,'pairs_ratio_long_short':pairs}
    raw={}
    for key,fn in methods.items():
        # Holdings may be chosen before start using pre-start history; only report selected period.
        history=nav_returns(prices,fn,fee)
        raw[key]=[r for r in history if start<=r['date']<=end]
    return raw

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--from',dest='start',default='2021-01-01');ap.add_argument('--to',dest='end',default='2026-10-23')
    ap.add_argument('--split',default='2025-01-01');ap.add_argument('--symbols',default=DEFAULT)
    ap.add_argument('--csv-dir',help='folder with SYMBOL.csv adjusted daily open/close; offline')
    ap.add_argument('--fee-bps',type=float,default=10,help='one-way per unit of portfolio-weight turnover')
    ap.add_argument('--output',default='/app/reports/candidates/v12')
    args=ap.parse_args(argv)
    if args.fee_bps<0 or args.start>=args.end or not args.start<args.split<=args.end:ap.error('invalid dates or fee')
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    symbols=list(dict.fromkeys(s.strip().upper() for s in args.symbols.split(',') if s.strip()))
    start_fetch=(dt.date.fromisoformat(args.start)-dt.timedelta(days=520)).isoformat()
    series={};errors={}
    for s in symbols:
        try:
            series[s]=csv_daily(s,args.csv_dir) if args.csv_dir else yahoo_daily(s,start_fetch,args.end,output/'cache')
            if len(series[s])<260:errors[s]=f'insufficient bars: {len(series[s])}'
        except Exception as exc:errors[s]=str(exc)[:250]
    dates=sorted(set().union(*(set(v) for v in series.values()))) if series else []
    prices={d:{s:v[d]['close'] for s,v in series.items() if d in v} for d in dates}
    if not dates:raise SystemExit('No prices available; check errors and network / supply --csv-dir')
    trades=build(prices,args.start,args.end,args.fee_bps)
    # SPY holding baseline from same data period.
    spy=[]
    for i in range(1,len(dates)):
        a,b=dates[i-1],dates[i]
        if args.start<=b<=args.end and 'SPY' in prices[a] and 'SPY' in prices[b]:spy.append({'date':b,'net_return':prices[b]['SPY']/prices[a]['SPY']-1})
    results={k:summarize(v,args.split) for k,v in trades.items()}
    results['etf_intraday_last_half_hour']={'status':'NOT_EVALUATED_NO_MULTIYEAR_5M_ARCHIVE','reason':'Yahoo 5-minute ~60 days; no fabricated multi-year result'}
    report={'status':'EXPLORATORY_ADAPTATIONS_NOT_ACADEMIC_REPRODUCTIONS','period':{'start':args.start,'end':args.end,'split':args.split},'source':'adjusted Yahoo daily OHLC' if not args.csv_dir else 'user-supplied adjusted daily CSV','fees_bps_one_way_per_weight':args.fee_bps,'market_data_errors':errors,'stock_symbols':symbols,'strategies':results,'benchmark_spy_buy_hold_gross':summarize(spy,args.split),'warnings':['No independent untouched holdout; split descriptive only after inspecting results.','Uses adjusted daily closes: close-to-close approximation, not exact next-open execution.','Yahoo adjusted data subject to corporate-action revisions and survivorship bias.','Pairs assume short availability, no borrow fees, no margin constraints; optimistic.','Adapted screening rules, not faithful original academic strategy replications.','No live orders or broker connection.']}
    (output/'summary.json').write_text(json.dumps(report,indent=2))
    with (output/'daily_returns.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['strategy','date','net_return','equity','turnover'])
        for name,vals in trades.items():
            for r in vals:w.writerow([name,r['date'],r['net_return'],r['equity'],r['turnover']])
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
