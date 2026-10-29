"""Single-process scheduler for day/swing research; never submits orders."""
import argparse
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from day_radar import run as day_run
from swing_radar import run as swing_run
from shadow_journal import capture

def main():
    p=argparse.ArgumentParser();p.add_argument('--interval-minutes',type=int,default=30)
    a=p.parse_args()
    if a.interval_minutes<15 or a.interval_minutes>240:raise SystemExit('Interval must be 15..240')
    if os.getenv('LIVE_TRADING_ENABLED','false').lower()!='false':raise SystemExit('Live forbidden')
    print('Dual radar: day and swing research only. No orders. NY weekdays, holidays not filtered.',flush=True)
    last_regular=0;last_eod=None
    while True:
        now=datetime.now(ZoneInfo('America/New_York'));minute=now.hour*60+now.minute
        if now.weekday()<5:
            if 570<=minute<960 and (time.monotonic()-last_regular>=a.interval_minutes*60):
                try:
                    swing_run(os.getenv('SWING_SYMBOLS','AAPL,MSFT,NVDA,AMD,GOOGL,AMZN,META,TSLA,AVGO,PLTR,SPY,QQQ'),'/app/reports/swing/latest.json')
                    result=day_run()
                    print('Day radar:',result['health'],len(result['candidates']),'orders=0',flush=True)
                except Exception as e:print('Research scan failed:',type(e).__name__,str(e)[:120],flush=True)
                last_regular=time.monotonic()
            if minute>=975 and last_eod!=now.date().isoformat():
                try:
                    snap=swing_run(os.getenv('SWING_SYMBOLS','AAPL,MSFT,NVDA,AMD,GOOGL,AMZN,META,TSLA,AVGO,PLTR,SPY,QQQ'),'/app/reports/swing/latest.json')
                    if snap.get('health')=='OK_RESEARCH_ONLY' and snap.get('paper_account',{}).get('status')=='READ_ONLY_DIAGNOSTIC_NO_ORDERS':
                        try: capture(snap)
                        except ValueError as e:print('Journal skipped:',str(e)[:150],flush=True)
                except Exception as e: print('EOD scan failed:',type(e).__name__,str(e)[:120],flush=True)
                last_eod=now.date().isoformat()
        time.sleep(60)

if __name__=='__main__':main()
