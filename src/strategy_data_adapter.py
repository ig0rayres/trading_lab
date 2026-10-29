"""Collective2 historical provider review; strictly read-only, fail closed.
Provider P&L is never fed into Paper P&L or eligibility approval.
"""
import argparse
import json
import math
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from strategy_intelligence import evaluate

NAMES={'148311109':'Solid Companies','132169961':'Easy Value','30415311':'ETF Timer'}
WINDOWS=(7,30,90,180)

def timestamp(value):
    if isinstance(value,str):
        match=re.fullmatch(r'/Date\((-?\d+)(?:[+-]\d{4})?\)/',value.strip())
        if match:
            value=int(match.group(1))
        elif value.strip().lstrip('-').isdigit():
            value=int(value.strip())
        elif re.fullmatch(r'\d{4}-\d{2}-\d{2}',value.strip()):
            return datetime.fromisoformat(value.strip()).replace(tzinfo=timezone.utc)
    if isinstance(value,(int,float)):
        v=float(value)
        if v>1e12:v/=1000
        return datetime.fromtimestamp(v,tz=timezone.utc)
    d=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    if d.tzinfo is None:raise ValueError('missing timezone')
    return d.astimezone(timezone.utc)

def num(value):
    if isinstance(value,bool): raise ValueError('invalid number')
    n=float(value)
    if not math.isfinite(n):raise ValueError('nonfinite')
    return n

def load(base,sid,kind):
    f=base/f'{sid}_{kind}.json'
    obj=json.loads(f.read_text())
    if str(obj.get('strategy_id'))!=sid or obj.get('dataset')!=kind:raise ValueError('mismatched dataset')
    raw=obj['raw']
    if not isinstance(raw,dict) or not isinstance(raw.get('Results'),list):raise ValueError('unexpected response')
    if raw.get('ResponseStatus',{}).get('ErrorCode') not in (0,'0',None,200,'200'):raise ValueError('api error')
    return raw['Results'],obj.get('fetched_at_utc')

def nested_equity(rows):
    if len(rows)!=1 or not isinstance(rows[0],dict):return None
    return rows[0].get('DailyEquity')

def review(base,now=None):
    now=now or datetime.now(timezone.utc)
    records=[]; observations=[]
    ids=sorted(set(f.name.split('_')[0] for f in base.glob('*_closed_trades.json') if f.name.split('_')[0].isdigit()))
    for sid in ids:
        rec={'provider_id':sid,'name':NAMES.get(sid,sid),'status':'INSUFFICIENT_DATA','eligible_for_copy':False,'reasons':[], 'windows':{}}
        try:
            trades,fetch_trades=load(base,sid,'closed_trades')
            if trades and isinstance(trades[0],dict): rec['trade_field_names']=sorted(trades[0].keys())[:40]
            rows,fetch_eq=load(base,sid,'daily_equity')
            equity=nested_equity(rows)
            if not isinstance(equity,list) or not equity: rec['reasons'].append('EQUITY_NOT_LIST')
            if isinstance(equity,list) and equity and isinstance(equity[0],dict):
                rec['equity_field_names']=sorted(equity[0].keys())[:40]
            # Dates/values are never guessed from unrelated fields.
            datekeys=('Date','date','EquityDate','dateTime','Time','Timestamp','StrategyEquityDate','EquityDateTime','dateUTC','DateTime','dateTimeUTC')
            valkeys=('EquityWithCosts','Equity','equity','StrategyEquity','Value','value','PortfolioEquity','EquityValue','TotalEquity','AccountEquity','StrategyValue')
            series=[]
            if isinstance(equity,list):
                for row in equity:
                    if not isinstance(row,dict):raise ValueError('equity row invalid')
                    datekey=next((k for k in datekeys if k in row),None)
                    valkey=next((k for k in valkeys if k in row),None)
                    if datekey is None or valkey is None:
                        rec['reasons'].append('UNRECOGNIZED_EQUITY_FIELDS')
                        break
                    d=timestamp(row[datekey]);v=num(row[valkey])
                    if v<=0 or d>now+timedelta(days=1):raise ValueError('invalid equity point')
                    series.append((d,v))
            series.sort()
            if any(series[i][0]<=series[i-1][0] for i in range(1,len(series))):raise ValueError('duplicate date')
            if series and (now-series[-1][0])>timedelta(days=10):rec['reasons'].append('STALE_EQUITY_HISTORY')
            for days in WINDOWS:
                start=now-timedelta(days=days)
                # Last observation ON OR BEFORE the window boundary, avoiding inflated returns.
                before=[x for x in series if x[0]<=start]
                during=[x for x in series if start<x[0]<=now]
                win={'closed_trades':0,'gross_reported':0,'commission_reported':0,'return_pct':None,'max_drawdown_pct':None,'baseline_at_utc':None,'last_point_at_utc':None}
                for t in trades:
                    try:
                        d=timestamp(t['CloseDate'])
                        if start<=d<=now:
                            win['closed_trades']+=1
                            win['gross_reported']+=num(t['ProfitLoss'])
                            win['commission_reported']+=num(t.get('Commission',0))
                    except (KeyError,TypeError,ValueError,OverflowError):
                        rec['reasons'].append('INVALID_TRADE_ROW')
                win['gross_reported']=round(win['gross_reported'],2)
                win['commission_reported']=round(win['commission_reported'],2)
                if before and during:
                    seq=[before[-1]]+during
                    win['baseline_at_utc']=seq[0][0].isoformat()
                    win['last_point_at_utc']=seq[-1][0].isoformat()
                    top=seq[0][1]; drawdown=0
                    for _,v in seq:
                        top=max(top,v);drawdown=max(drawdown,(top-v)/top*100)
                    win['return_pct']=round((seq[-1][1]/seq[0][1]-1)*100,3)
                    win['max_drawdown_pct']=round(drawdown,3)
                rec['windows'][str(days)]=win
            w=rec['windows']['180']
            if w['return_pct'] is None:rec['reasons'].append('NO_180D_BASELINE')
            # Cash flows can distort simple equity ratio; mark as a research-only proxy.
            rec['return_method']='EQUITY_WITH_COSTS_SIMPLE_RATIO_UNADJUSTED_FOR_FLOWS'
            if w['closed_trades']<30:rec['reasons'].append('LOW_180D_SAMPLE')
            if not rec['reasons']:
                rec['status']='HISTORY_REVIEWED_NOT_APPROVED'
            rec['reasons']=sorted(set(rec['reasons']))
            rec['fetched_at_utc']={'equity':fetch_eq,'trades':fetch_trades}
        except (ValueError,TypeError,KeyError,OSError,OverflowError) as exc:
            rec['reasons'].append('INVALID_OR_MISSING_SOURCE_DATA')
            rec['source_error_type']=type(exc).__name__
            # Bounded diagnostic: no raw values, account data or credentials.
            rec['source_error_detail']=str(exc)[:160]
        records.append(rec)
        observations.append({'id':'c2:'+sid,'evidence_verified':False,'execution_reconciled':False,
            'prior_paper_approved':False,'trades':[], 'risk_breach':False,'stale_feed':bool('STALE_EQUITY_HISTORY' in rec['reasons'])})
    return {'mode':'HISTORICAL_PROVIDER_REVIEW_READ_ONLY','as_of':now.isoformat(),
            'providers':records,'orders_sent':0,'execution_authorized':False,
            'warning':'Provider equity is not Paper P&L; no provider auto-approved.'}, {'strategies':observations}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--raw-dir',default='/app/reports/providers/raw')
    ap.add_argument('--output-dir',default='/app/reports/intelligence')
    args=ap.parse_args()
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    report,obs=review(Path(args.raw_dir))
    (out/'provider-180d-latest.json').write_text(json.dumps(report,indent=2))
    (out/'provider-observations.json').write_text(json.dumps(obs,indent=2))
    # Descriptive research leaderboard; not approved signals or providers.
    ranked=[r for r in report['providers'] if r['windows'].get('180',{}).get('return_pct') is not None]
    ranked.sort(key=lambda r: (r['windows']['180']['return_pct'], -r['windows']['180']['max_drawdown_pct']), reverse=True)
    leaderboard={'mode':'PROVIDER_RESEARCH_RANKING_ONLY','as_of':report['as_of'],
       'ranking_basis':'180d simple equity ratio, unadjusted for deposits or withdrawals',
       'candidates_with_numeric_results':len(ranked),
       'top_10_research':[{'provider_id':r['provider_id'],'name':r['name'],
           'return_pct':r['windows']['180']['return_pct'],
           'max_drawdown_pct':r['windows']['180']['max_drawdown_pct'],
           'closed_trades':r['windows']['180']['closed_trades'],
           'issues':r['reasons']} for r in ranked[:10]],
       'copy_approved':[],'orders_sent':0,'execution_authorized':False}
    (out/'provider-research-top10-latest.json').write_text(json.dumps(leaderboard,indent=2))
    summary={'providers':len(report['providers']),'eligible_for_copy':0,'cadences':{}}
    for cadence in ('daily','weekly','monthly'):
        item=evaluate(obs,cadence)
        (out/(cadence+'-latest.json')).write_text(json.dumps(item,indent=2))
        archive=out/(cadence+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
        archive.write_text(json.dumps(item,indent=2))
        summary['cadences'][cadence]={x['status']:sum(1 for v in item['strategies'] if v['status']==x['status']) for x in item['strategies']}
    print(json.dumps({'mode':'CONTINUOUS_REVIEW_READ_ONLY','summary':summary,'output_dir':str(out),'orders_sent':0,'execution_authorized':False},indent=2))

if __name__=='__main__':main()
