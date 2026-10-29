"""Continuous read-only strategy intelligence. Input evidence is supplied as JSON.
No market/broker access; no automatic authorization to trade.
"""
import argparse
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path

CADENCES = ('daily', 'weekly', 'monthly')

def stamp(s):
    d = datetime.fromisoformat(str(s).replace('Z','+00:00'))
    if d.tzinfo is None: raise ValueError('Timezone required')
    return d.astimezone(timezone.utc)

def evaluate(data, cadence, now=None):
    if cadence not in CADENCES: raise ValueError('Unsupported cadence')
    now=now or datetime.now(timezone.utc)
    windows = {'daily':1, 'weekly':7, 'monthly':30}
    cutoff=now-timedelta(days=windows[cadence])
    results=[]
    seen=set()
    for s in data.get('strategies',[]):
        sid=s['id']
        if sid in seen: raise ValueError('Duplicate strategy ID')
        seen.add(sid)
        events=[]
        invalid=False
        for t in s.get('trades',[]):
            try:
                d=stamp(t['closed_at']); pnl=float(t['net_pnl_brl'])
                if not math.isfinite(pnl) or d>now: raise ValueError('Invalid trade')
                if cutoff <= d <= now: events.append((d,pnl))
            except (KeyError,ValueError,TypeError,OverflowError): invalid=True
        events.sort()
        pnl=sum(x[1] for x in events)
        losses=sum(1 for _,x in events if x<0)
        # Explicit conservative risk policy: no evidence never means approved.
        reasons=[]
        if invalid: reasons.append('INVALID_TRADE_DATA')
        if s.get('evidence_verified') is not True: reasons.append('UNVERIFIED_EVIDENCE')
        if s.get('execution_reconciled') is not True: reasons.append('UNRECONCILED_EXECUTION')
        if s.get('risk_breach') is True: reasons.append('RISK_BREACH')
        if s.get('stale_feed') is True: reasons.append('STALE_SIGNAL_FEED')
        if pnl <= -150: reasons.append('LOSS_THRESHOLD_BREACHED')
        if not events: reasons.append('NO_CLOSED_TRADES_IN_WINDOW')
        if s.get('open_orders_unknown') is True: reasons.append('UNKNOWN_OPEN_ORDER_STATE')
        hard = {'INVALID_TRADE_DATA','RISK_BREACH','STALE_SIGNAL_FEED','LOSS_THRESHOLD_BREACHED','UNKNOWN_OPEN_ORDER_STATE'}
        status='SUSPENDED' if any(r in hard for r in reasons) else 'OBSERVATION'
        # Never promote solely because of a short profitable sample.
        if not reasons and s.get('prior_paper_approved') is True:
            status='PAPER_ELIGIBLE'
        results.append({'strategy_id':sid,'status':status,'reasons':reasons,'closed_trades':len(events),
                        'net_pnl_brl':round(pnl,2),'losing_trades':losses})
    return {'mode':'STRATEGY_INTELLIGENCE_READ_ONLY','cadence':cadence,'as_of':now.isoformat(),
            'window_start':cutoff.isoformat(),'strategies':results,'orders_sent':0,
            'execution_authorized':False,
            'warning':'Status is advisory only until enforced by gateway. No strategy is promoted without prior Paper approval.'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--cadence',required=True,choices=CADENCES)
    p.add_argument('--input',required=True)
    p.add_argument('--output-dir',default='/app/reports/intelligence')
    args=p.parse_args()
    data=json.loads(Path(args.input).read_text())
    report=evaluate(data,args.cadence)
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    target=out/(args.cadence+'-latest.json')
    archive=out/(args.cadence+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    serialized=json.dumps(report,indent=2)
    archive.write_text(serialized)
    target.write_text(serialized)
    print(serialized)

if __name__=='__main__': main()
