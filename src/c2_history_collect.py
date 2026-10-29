#!/usr/bin/env python3
"""Read-only Collective2 API4 historical data collector. Never submits trades."""
import argparse, datetime as dt, json, os, pathlib, urllib.parse, urllib.request, urllib.error
BASE = 'https://api4-general.collective2.com'
PATHS = {
    'daily_equity': '/Strategies/GetStrategyHistoricalDailyEquity',
    'monthly_equity': '/Strategies/GetStrategyHistoricalEquity',
    'closed_trades': '/Strategies/GetStrategyHistoricalClosedTrades',
}
def fetch(path, params, token):
    url = BASE + path + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'Authorization':'Bearer '+token, 'Accept':'application/json', 'User-Agent':'TradingLab-ReadOnly-C2-History/1.0'})
    with urllib.request.urlopen(req, timeout=25) as res:
        return json.load(res)
def main():
    p=argparse.ArgumentParser(description='Fetch raw read-only history from Collective2 API4; no orders')
    p.add_argument('--strategy-id', type=int, required=True, action='append', help='C2 numeric strategy ID; repeat to retrieve multiple')
    p.add_argument('--output-dir', default='/app/reports/providers/raw_collective2')
    a=p.parse_args()
    token=os.environ.get('C2_API4_KEY','').strip()
    if not token: p.error('C2_API4_KEY must be set in EasyPanel environment; never paste it into chat')
    root=pathlib.Path(a.output_dir); root.mkdir(parents=True,exist_ok=True)
    summary=[]
    for sid in sorted(set(a.strategy_id)):
        if sid <= 0: p.error('strategy IDs must be positive')
        for key,path in PATHS.items():
            try:
                obj=fetch(path, {'StrategyId':sid,'CommissionPlan':'0'},token)
                status=obj.get('ResponseStatus') or {}
                if status.get('Errors') or str(status.get('ErrorCode','')) in ('401','403','500'):
                    summary.append({'strategy_id':sid,'dataset':key,'status':'API_REPORTED_ERROR','message':str(status.get('Message',''))[:160]})
                    continue
                fn=root / f'{sid}_{key}.json'
                fn.write_text(json.dumps({'strategy_id':sid,'dataset':key,'fetched_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'raw':obj},indent=2))
                summary.append({'strategy_id':sid,'dataset':key,'status':'SAVED','rows':len(obj.get('Results') or []),'file':str(fn)})
            except urllib.error.HTTPError as e:
                summary.append({'strategy_id':sid,'dataset':key,'status':'HTTP_ERROR','http_code':e.code})
            except Exception as e:
                summary.append({'strategy_id':sid,'dataset':key,'status':'FETCH_ERROR','error_type':type(e).__name__})
    print(json.dumps({'mode':'COLLECTIVE2_HISTORY_READ_ONLY','orders_sent':0,'results':summary},indent=2))
if __name__=='__main__':main()
