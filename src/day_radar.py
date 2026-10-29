"""Read-only 5-minute day-trading diagnostic. No order route, no approved trading edge."""
import argparse
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo('America/New_York')
DEFAULT = 'AAPL,MSFT,NVDA,AMD,TSLA,PLTR,SPY,QQQ'


def bars_from_yahoo(payload, symbol, now_utc):
    result = (payload.get('chart',{}).get('result') or [None])[0]
    if not result: raise ValueError('Missing Yahoo chart data')
    quote = result['indicators']['quote'][0]
    ticks = result.get('timestamp') or []
    bars=[]
    for i, stamp in enumerate(ticks):
        instant=datetime.fromtimestamp(stamp, timezone.utc)
        if instant + timedelta(minutes=5)>now_utc: continue  # incomplete bar is NOT evidence
        loc=instant.astimezone(NY)
        if not (loc.weekday()<5 and (9,30)<=(loc.hour,loc.minute)<(16,0)):continue
        try:
            o,h,l,c,v=[quote[k][i] for k in ('open','high','low','close','volume')]
            if any(x is None for x in (o,h,l,c,v)) or min(o,h,l,c)<=0 or h<l or v<0:continue
            bars.append({'day':loc.date().isoformat(),'time':loc.strftime('%H:%M'),
                         'open':float(o),'high':float(h),'low':float(l),'close':float(c),'volume':int(v)})
        except (IndexError,KeyError,TypeError,ValueError):continue
    return bars


def assess(symbol, bars, now_ny):
    """Detect first completed-bar breakout per direction; no approvals or orders."""
    day=now_ny.date().isoformat()
    today=sorted([b for b in bars if b['day']==day], key=lambda x:x['time'])
    common=['NO_VALIDATED_INTRADAY_EDGE','PRIMARY_SOURCE_CATALYST_NOT_VERIFIED',
            'EXECUTION_RISK_GATES_NOT_IMPLEMENTED']
    result={'symbol':symbol,'session':day,'observed_bars':len(today),
            'signal':'NO_TRADE','order_eligible':False,'blockers':[],
            'research_setup':None,'research_setups':{'LONG':None,'SHORT':None},
            'directions':{side:{'signal':'NO_TRADE','order_eligible':False,
                                'blockers':[],'research_setup':None} for side in ('LONG','SHORT')}}
    def reject_all(reason):
        result['blockers'].append(reason)
        for direction in result['directions'].values():direction['blockers'].append(reason)
        return result
    if now_ny.weekday()>=5:return reject_all('NOT_A_WEEKDAY')
    if not (9,50)<=(now_ny.hour,now_ny.minute)<(16,0):return reject_all('OUTSIDE_ORB_WINDOW')
    opening=[b for b in today if b['time'] in ('09:30','09:35','09:40')]
    if len(opening)!=3:return reject_all('OPENING_BARS_MISSING')
    if len(set(b['time'] for b in opening))!=3:return reject_all('OPENING_BARS_DUPLICATED')
    hi=max(b['high'] for b in opening);lo=min(b['low'] for b in opening)
    post=[b for b in today if b['time']>='09:45']
    if not post:return reject_all('NO_COMPLETED_CONFIRMATION_BAR')
    for side in ('LONG','SHORT'):
        first=next((b for b in post if b['close']>hi),None) if side=='LONG' else next((b for b in post if b['close']<lo),None)
        direction=result['directions'][side]
        if first:
            setup={'kind':'ORB_15M_BREAKOUT' if side=='LONG' else 'ORB_15M_BREAKDOWN',
                   'side':side,'first_confirmation_bar_ny':first['time'],
                   'confirmation_available_at_ny':(datetime.strptime(first['time'],'%H:%M')+timedelta(minutes=5)).strftime('%H:%M'),
                   'bar_time_convention':'START_TIME_5M',
                   'opening_range_high':round(hi,4),'opening_range_low':round(lo,4),
                   'confirmation_close':round(first['close'],4)}
            direction['research_setup']=setup
            result['research_setups'][side]=setup
            if side=='LONG':result['research_setup']=setup  # legacy compatibility
        else:direction['blockers'].append('NO_ORB_BREAKOUT' if side=='LONG' else 'NO_ORB_BREAKDOWN')
        direction['blockers'].extend(common)
        if side=='SHORT':direction['blockers'].extend(['SHORT_BORROW_AND_MARGIN_NOT_VERIFIED','SHORT_GAP_AND_RECALL_RISK'])
    result['blockers']=list(dict.fromkeys(b for side in ('LONG','SHORT') for b in result['directions'][side]['blockers']))
    return result


def fetch_live(symbol, now_utc):
    url='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(symbol,safe='')+'?range=5d&interval=5m'
    req=urllib.request.Request(url,headers={'User-Agent':os.getenv('MARKET_USER_AGENT','TradingLabResearch read-only'),
                                           'Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as r:
        return bars_from_yahoo(json.load(r),symbol,now_utc)


def run(symbols=None,now_utc=None,fetch=fetch_live,output='/app/reports/day/latest.json'):
    if os.getenv('LIVE_TRADING_ENABLED','false').lower()!='false':raise ValueError('Live trading prohibited')
    if os.getenv('ALPACA_PAPER_TRADE','true').lower()!='true':raise ValueError('Paper mode required')
    now_utc=now_utc or datetime.now(timezone.utc)
    now_ny=now_utc.astimezone(NY)
    universe=list(dict.fromkeys((symbols or DEFAULT.split(','))))
    if not universe or len(universe)>25 or any(not (s.isascii() and s.isalnum() and 1<=len(s)<=5) for s in universe):
        raise ValueError('Invalid universe')
    report={'mode':'DAY_RESEARCH_ONLY_NO_ORDERS','generated_at_utc':now_utc.isoformat(),
            'market_time_ny':now_ny.isoformat(),'broker_orders_sent':0,'trades_simulated':0,
            'capital_ceiling_brl':5000,'risk_limit_brl_per_trade':50,'max_combined_positions':3,
            'strategy':'15m_ORB_LONG_SHORT_diagnostic_only','candidates':[],'errors':[],
            'limitations':['Not a verified alpha strategy','Yahoo unofficial/delayed data',
                           'No point-in-time verified news','No VWAP from unverified intraday feed',
                           'No fill simulation and no risk enforcement for broker orders',
                           'SHORT research does not validate shortability, borrowing fees, locate or margin',
                           'Opposite-direction setups may occur at different times; not simultaneous authorization',
                           'Yahoo 5m timestamps are bar START; signal is known only after the bar closes']}
    for symbol in universe:
        try:report['candidates'].append(assess(symbol,fetch(symbol,now_utc),now_ny))
        except Exception as e:
            report['errors'].append({'symbol':symbol,'kind':type(e).__name__})
            report['candidates'].append({'symbol':symbol,'signal':'NO_TRADE',
                                          'order_eligible':False,'blockers':['MARKET_DATA_UNAVAILABLE']})
    report['health']='OK_RESEARCH_ONLY' if not report['errors'] else 'PARTIAL_DATA'
    if output:
        path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(report,indent=2)+'\n');tmp.replace(path)
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('--symbols',default=os.getenv('DAY_SYMBOLS',DEFAULT))
    p.add_argument('--output',default='/app/reports/day/latest.json')
    args=p.parse_args();result=run([s.strip().upper() for s in args.symbols.split(',') if s.strip()],output=args.output)
    print(json.dumps({'health':result['health'],'candidates':len(result['candidates']),
                      'setups':sum(bool(v) for c in result['candidates'] for v in c.get('research_setups',{}).values()),
                      'long_setups':sum(bool(c.get('research_setups',{}).get('LONG')) for c in result['candidates']),
                      'short_setups':sum(bool(c.get('research_setups',{}).get('SHORT')) for c in result['candidates']),
                      'errors':len(result['errors']),'orders_sent':0,'output':args.output}))

if __name__=='__main__':main()
