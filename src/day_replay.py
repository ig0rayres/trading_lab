"""Conservative historical ORB experiment. Research ONLY. No broker imports or order route.

A signal is known after a fully closed 5m bar; enter at the NEXT candle OPEN.
Includes 5bps each side by default. Fills and stops in reality may be worse.
"""
import argparse
import json
import math
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from day_radar import bars_from_yahoo, DEFAULT, NY


def fetch_history(symbol, now_utc):
    url='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(symbol,safe='')+'?range=60d&interval=5m'
    req=urllib.request.Request(url,headers={'User-Agent':os.getenv('MARKET_USER_AGENT','TradingLabResearch research-only'),'Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=25) as r:return bars_from_yahoo(json.load(r),symbol,now_utc)


def replay_day(bars, side, *, budget=1000.0, risk=10.0, cost_bps=5.0, reward_r=2.0, earliest="09:45", latest="15:40", min_break_pct=0.0, min_rel_volume=0.0):
    """One candidate per side. No fills assumed until next 5m candle's open."""
    ts={b['time']:i for i,b in enumerate(bars)}
    if not all(t in ts for t in ('09:30','09:35','09:40')):return {'status':'MISSING_OPENING'}
    bars=sorted(bars,key=lambda b:b['time'])
    ts={b['time']:i for i,b in enumerate(bars)}
    if ts['09:30']!=0 or ts['09:35']!=1 or ts['09:40']!=2:return {'status':'NONCONTIGUOUS_OPENING'}
    opening=bars[:3];hi=max(x['high'] for x in opening);lo=min(x['low'] for x in opening)
    # Require contiguous five-minute candles through the point of confirmation and entry.
    def minute(t):return int(t[:2])*60+int(t[3:])
    for i in range(1,len(bars)):
        if minute(bars[i]['time'])-minute(bars[i-1]['time'])!=5:return {'status':'GAPPED_SESSION'}
    candidates=[i for i in range(3,len(bars)) if earliest<=bars[i]['time']<=latest and
                (bars[i]['close']>hi*(1+min_break_pct/100) if side=='LONG' else bars[i]['close']<lo*(1-min_break_pct/100)) and
                (not min_rel_volume or (sum(x['volume'] for x in bars[max(0,i-3):i])>0 and
                  bars[i]['volume'] >= min_rel_volume*(sum(x['volume'] for x in bars[max(0,i-3):i])/len(bars[max(0,i-3):i]))))]
    if not candidates:return {'status':'NO_SIGNAL'}
    j=candidates[0]
    if j+1>=len(bars):return {'status':'NO_NEXT_BAR'}
    entry=bars[j+1]['open']
    stop=lo if side=='LONG' else hi
    distance=(entry-stop) if side=='LONG' else (stop-entry)
    if distance<=0:return {'status':'INVALID_STOP_GEOMETRY'}
    qty=math.floor(min(budget/entry,risk/distance))
    if qty<1:return {'status':'SIZE_TOO_SMALL','confirmation_bar_start':bars[j]['time'],'first_actionable_bar_start':bars[j+1]['time']}
    target=entry+reward_r*distance if side=='LONG' else entry-reward_r*distance
    if target<=0:return {'status':'INVALID_TARGET'}
    outcome='END_OF_DAY';exit_price=None
    # At entry bar open, a price gap can leap beyond stop; charge the worse open.
    for bar in bars[j+1:]:
        if bar['time']>'15:55':break
        o,h,l=bar['open'],bar['high'],bar['low']
        if side=='LONG':
            if o<=stop:exit_price=o;outcome='GAP_STOP';break
            if l<=stop:exit_price=stop;outcome='STOP';break
            if h>=target:exit_price=target;outcome='TARGET';break
        else:
            if o>=stop:exit_price=o;outcome='GAP_STOP';break
            if h>=stop:exit_price=stop;outcome='STOP';break
            if l<=target:exit_price=target;outcome='TARGET';break
    if exit_price is None:
        if not bars or bars[-1]['time']!='15:55':return {'status':'INCOMPLETE_EOD'}
        exit_price=bars[-1]['close']
    gross=(exit_price-entry)*qty*(1 if side=='LONG' else -1)
    cost=(entry+exit_price)*qty*cost_bps/10000
    net=gross-cost
    return {'status':'EVALUATED','side':side,'confirmation_bar_start':bars[j]['time'],
            'confirmation_available_at':(datetime.strptime(bars[j]['time'],'%H:%M')+timedelta(minutes=5)).strftime('%H:%M'),
            'first_actionable_bar_start':bars[j+1]['time'],'entry':round(entry,4),
            'stop':round(stop,4),'target':round(target,4),'shares_integer':qty,
            'outcome':outcome,'gross_usd':round(gross,4),'cost_usd':round(cost,4),
            'net_usd':round(net,4),'net_r':round(net/(qty*distance),4)}


def run(symbols=None, fetch=fetch_history, now_utc=None, sessions=20,output='/app/reports/day/historical-long-short.json'):
    if os.getenv('LIVE_TRADING_ENABLED','false').lower()!='false':raise ValueError('Live is forbidden')
    if os.getenv('ALPACA_PAPER_TRADE','true').lower()!='true':raise ValueError('Paper environment required')
    if not 1<=sessions<=40:raise ValueError('Sessions must be 1..40')
    now_utc=now_utc or datetime.now(timezone.utc)
    today=now_utc.astimezone(NY).date().isoformat()
    symbols=symbols or DEFAULT.split(',')
    out={'mode':'HISTORICAL_ORB_LONG_SHORT_RESEARCH_ONLY','as_of_utc':now_utc.isoformat(),
         'parameters':{'capital_usd':1000,'risk_usd':10,'max_combined_positions':3,'round_trip_cost_bps':10,'reward_r':2},
         'limitations':['No historical point-in-time catalysts, borrowing availability, borrow fees or validated strategy edge',
                        'Simulated 5-minute OHLC execution, no real fills; gaps can exceed stop risk',
                        'Independent candidate outcomes; NOT a simultaneous 3-position portfolio simulation',
                        'Yahoo bars unofficial; selected earlier dates only; absent/incomplete sessions excluded'],
         'orders_sent':0,'results':[],'errors':[]}
    for symbol in symbols:
        try:
            bars=fetch(symbol,now_utc)
            byday={}
            for b in bars:
                if b['day']<today:byday.setdefault(b['day'],[]).append(b)
            for day in sorted(byday)[-sessions:]:
                daybars=sorted(byday[day],key=lambda x:x['time'])
                for side in ('LONG','SHORT'):
                    x=replay_day(daybars,side)
                    out['results'].append({'symbol':symbol,'session':day,'side':side,**x})
        except Exception as e:out['errors'].append({'symbol':symbol,'error':type(e).__name__})
    out['evaluated']=sum(r['status']=='EVALUATED' for r in out['results'])
    out['positive']=sum(r.get('net_usd',0)>0 for r in out['results'] if r['status']=='EVALUATED')
    out['negative']=sum(r.get('net_usd',0)<0 for r in out['results'] if r['status']=='EVALUATED')
    out['health']='OK_RESEARCH_ONLY' if not out['errors'] else 'PARTIAL_DATA'
    if output:
        p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
        t=p.with_suffix('.tmp');t.write_text(json.dumps(out,indent=2)+'\n');t.replace(p)
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--sessions',type=int,default=20)
    p.add_argument('--symbols',default=DEFAULT)
    p.add_argument('--output',default='/app/reports/day/historical-long-short.json')
    a=p.parse_args()
    x=run(symbols=[s.strip().upper() for s in a.symbols.split(',') if s.strip()],sessions=a.sessions,output=a.output)
    print(json.dumps({k:x[k] for k in ('health','evaluated','positive','negative','orders_sent','errors')}))

if __name__=='__main__':main()
