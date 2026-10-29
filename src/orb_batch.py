#!/usr/bin/env python3
"""One-session ORB event replay. Research only; not a historical edge estimate.

Uses upstream watchlist as SIGNAL SOURCE and independently obtains Yahoo candles.
Never changes upstream files, never contacts a broker. Pure stdlib.
"""
import argparse, csv, datetime as dt, json, os, sys, time, urllib.request, urllib.error
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from pathlib import Path
from zoneinfo import ZoneInfo

NY=ZoneInfo('America/New_York')
CENT=Decimal('0.01')

def cent(x):return Decimal(str(x)).quantize(CENT, rounding=ROUND_HALF_UP)
def down(x):return Decimal(str(x)).quantize(CENT, rounding=ROUND_FLOOR)
def fetch(symbol, date, cache, pause, refresh=False):
    cache.mkdir(parents=True,exist_ok=True)
    saved=cache/(symbol.replace('/','_')+'.json')
    if saved.exists() and not refresh: return json.loads(saved.read_text()), 'cache'
    url='https://query2.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(symbol)+'?range=5d&interval=5m&includePrePost=false'
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; research-lab/0.4)'})
    try:
        with urllib.request.urlopen(req,timeout=20) as response: data=json.load(response)
    except (urllib.error.URLError, TimeoutError) as exc: raise ValueError('FETCH_ERROR: '+str(exc))
    saved.write_text(json.dumps(data))
    if pause: time.sleep(pause)
    return data,'yahoo'

def bars_for_date(data,date, as_of=None):
    results=data['chart']['result']
    if not results:raise ValueError('EMPTY_RESPONSE')
    result=results[0]; ts=result.get('timestamp') or []
    quotes=result['indicators']['quote'][0]
    bars=[]
    for i,t in enumerate(ts):
        local=dt.datetime.fromtimestamp(t,NY)
        if local.date().isoformat()!=date or not dt.time(9,30)<=local.time()<dt.time(16,0):continue
        # Reject Yahoo's in-progress tick and future/incomplete candles.
        if local.minute % 5 != 0 or local.second != 0:continue
        if as_of is not None and local + dt.timedelta(minutes=5) > as_of:continue
        vals={k:quotes.get(k,[None]*len(ts))[i] for k in ('open','high','low','close','volume')}
        if any(vals[x] is None for x in ('open','high','low','close')):continue
        bars.append({'start':local,'end':local+dt.timedelta(minutes=5),**vals})
    bars.sort(key=lambda b:b['start'])
    if len({b['start'] for b in bars})!=len(bars):raise ValueError('DUPLICATE_BARS')
    return bars

def eval_hit(hit,bars,date,target_r,fee_bps,slip_bps, intraday=False):
    signal=hit['at']; signal_dt=dt.datetime.strptime(date+' '+signal,'%Y-%m-%d %I:%M %p').replace(tzinfo=NY)
    # 'at' is candle close (not start). We can enter only on the next 5m bar open.
    entry_bar=next((i for i,b in enumerate(bars) if b['start']==signal_dt),None)
    if entry_bar is None:raise ValueError('MISSING_NEXT_BAR')
    if signal_dt.time()>=dt.time(15,30):raise ValueError('LATE_SIGNAL')
    if bars[entry_bar]['end']>dt.datetime.combine(signal_dt.date(),dt.time(15,55),NY):raise ValueError('TOO_LATE')
    # Verify all candles from entry until close are complete and continuous (Yahoo may lag).
    if bars[-1]['end'].time()<dt.time(15,55) and not intraday:raise ValueError('SESSION_NOT_FINISHED')
    stop=down((Decimal(str(hit['or_high']))+Decimal(str(hit['or_low'])))/2)
    signal_price=Decimal(str(hit['price']))
    if signal_price<=stop:raise ValueError('NONPOSITIVE_SIGNAL_RISK')
    raw=Decimal(str(bars[entry_bar]['open']))
    if raw<=0:raise ValueError('BAD_OPEN')
    entry=raw*(1+Decimal(str(slip_bps))/10000)
    if entry<=stop:raise ValueError('GAP_BELOW_STOP')
    risk=entry-stop
    target=cent(entry+Decimal(str(target_r))*risk)
    # Preserve gap through stop with open execution; if same candle touches both => stop.
    reason='flat'; exit_raw=None; exit_dt=None
    flat=dt.datetime.combine(signal_dt.date(),dt.time(15,55),NY)
    prev=None
    for b in bars[entry_bar:]:
        if b['start']>=flat:break
        if prev is not None and b['start']!=prev:raise ValueError('GAPPED_CANDLES')
        prev=b['end']
        op=Decimal(str(b['open'])); lo=Decimal(str(b['low'])); hi=Decimal(str(b['high']))
        if op<=stop:exit_raw=op;reason='stop_gap';exit_dt=b['start'];break
        if lo<=stop:exit_raw=stop;reason='stop';exit_dt=b['end'];break
        if hi>=target:exit_raw=target;reason='target';exit_dt=b['end'];break
        if b['end']==flat:exit_raw=Decimal(str(b['close']));reason='flat';exit_dt=flat;break
    if exit_raw is None:
        if not intraday:raise ValueError('MISSING_FLAT_CANDLE')
        if prev is None:raise ValueError('MISSING_ENTRY_CANDLES')
        exit_raw=Decimal(str(bars[-1]['close']))
        exit_dt=bars[-1]['end']
        reason='mark_to_market_partial'
    exit_fill=exit_raw*(1-Decimal(str(slip_bps))/10000)
    fees=(entry+exit_fill)*Decimal(str(fee_bps))/10000
    pnl=exit_fill-entry-fees
    return dict(symbol=hit['symbol'],date=date,signal_at=signal_dt.isoformat(),entry_at=bars[entry_bar]['start'].isoformat(),
       signal_price=str(signal_price),entry_fill=round(float(entry),5),stop=str(stop),target=str(target),
       exit_at=exit_dt.isoformat(),exit_reason=reason,exit_fill=round(float(exit_fill),5),
       pnl_per_share=round(float(pnl),5),net_pct=round(100*float(pnl/entry),4),
       net_r=round(float(pnl/risk),4),target_r=target_r,fee_bps_per_side=fee_bps,slippage_bps_per_side=slip_bps,
       result_type=('PARTIAL_INTRADAY' if intraday else 'FINAL_SESSION'),
       as_of=bars[-1]['end'].isoformat())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--watchlist',required=True);ap.add_argument('--output',required=True)
    ap.add_argument('--date',default='2026-10-26');ap.add_argument('--fee-bps',type=float,default=5)
    ap.add_argument('--slippage-bps',type=float,default=5);ap.add_argument('--pause',type=float,default=0.2)
    ap.add_argument('--limit',type=int,default=0,help='0 means all hits; positive for connectivity test')
    ap.add_argument('--intraday',action='store_true',help='Evaluate only already completed bars; unresolved trades marked to market, not final')
    args=ap.parse_args()
    if args.fee_bps<0 or args.slippage_bps<0:ap.error('costs cannot be negative')
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    watch=json.loads(Path(args.watchlist).read_text()); hits=watch.get('hits',[])
    if args.limit>0:hits=hits[:args.limit]
    trades=[]; errors=[]
    now=dt.datetime.now(NY)
    intraday_now=now if args.intraday else None
    if args.intraday and args.date!=now.date().isoformat():
        ap.error('--intraday is only allowed for current NY trading date')
    for index,h in enumerate(hits,1):
        symbol=h.get('symbol','?')
        try:
            data,source=fetch(symbol,args.date,out/'cache',args.pause,refresh=(args.date==now.date().isoformat()))
            bars=bars_for_date(data,args.date,as_of=intraday_now)
            if not bars:raise ValueError('NO_SESSION_BARS')
            for r in (1,2): trades.append(eval_hit(h,bars,args.date,r,args.fee_bps,args.slippage_bps,intraday=args.intraday))
        except (ValueError,KeyError,IndexError,TypeError,decimal.InvalidOperation) as exc:
            errors.append({'symbol':symbol,'error':str(exc)})
        if index%10==0:print('Processed',index,'/',len(hits),'signals',flush=True)
    fields=['symbol','date','signal_at','entry_at','signal_price','entry_fill','stop','target','exit_at','exit_reason','exit_fill','pnl_per_share','net_pct','net_r','target_r','fee_bps_per_side','slippage_bps_per_side','result_type','as_of']
    with (out/'trades.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(trades)
    by={}
    for r in (1,2):
        s=[t for t in trades if t['target_r']==r]
        wins=sum(t['pnl_per_share']>0 for t in s);gain=sum(max(0,t['net_r']) for t in s);loss=-sum(min(0,t['net_r']) for t in s)
        by[f'{r}R']={'trades':len(s),'win_rate_pct':round(100*wins/len(s),2) if s else None,
          'mean_net_r':round(sum(t['net_r'] for t in s)/len(s),4) if s else None,
          'profit_factor':round(gain/loss,4) if loss else None}
    summary={'status':('PARTIAL_INTRADAY_NOT_REALIZED' if args.intraday else 'EXPLORATORY_ONLY_NOT_VALIDATED'),'date':args.date,'signals_requested':len(hits),'cutoff_ny':(intraday_now.isoformat() if intraday_now else None),'unresolved_marked_to_market':sum(t['exit_reason']=='mark_to_market_partial' for t in trades),'symbols_with_results':len(trades)//2,
      'symbols_with_errors':len(errors),'strategies':by,'assumptions':{'entry':'next bar open after signal timestamp','flat':'15:55 ET',
      'stop':'opening range midpoint rounded down to cent','both_touched':'stop first','fees_bps_per_side':args.fee_bps,
      'slippage_bps_per_side':args.slippage_bps},
      'warnings':['Single day of signals selected from daily watchlist; severe selection and survivorship biases.',
      'Yahoo 5m bars are unofficial; intrabar ordering and fills unknown.',
      'Net returns are per-share hypotheticals, not portfolio or capital-constrained performance.',
      'Partial results mark unresolved positions to market and are not completed trades.' if args.intraday else 'A successful run does not establish profitable strategy or authorize live trading.']}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    (out/'errors.json').write_text(json.dumps(errors,indent=2))
    print(json.dumps(summary,indent=2))
    return 0 if trades else 2

if __name__=='__main__':
    import decimal, urllib.parse
    sys.exit(main())
