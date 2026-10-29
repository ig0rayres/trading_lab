"""Explicit, single-order Alpaca Paper gateway. No automation, no live endpoint.

This does not infer a trading edge. Signal evidence and fresh price must be
prepared independently; unverified news_cycle outputs never qualify.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.request import Request, urlopen

from paper_audit import PAPER_URL, get_json, validate_env, amount

ALLOWED_KEYS = {'symbol','side','asset_class','event_id','primary_source_url',
                'event_verified_at_utc','price_observed_at_utc','entry','stop','target',
                'quantity','event_verified','reaction_confirmed','news_first'}
LOG = Path('/app/reports/paper/submissions.jsonl')

def parse_time(x):
    d = datetime.fromisoformat(str(x).replace('Z','+00:00'))
    if d.tzinfo is None:
        raise ValueError('Naive timestamp')
    return d.astimezone(timezone.utc)

def fingerprint(ticket):
    packed=json.dumps(ticket,sort_keys=True,separators=(',',':'))
    return hashlib.sha256(packed.encode()).hexdigest()[:24]

def ticket_gate(t, fx, now=None):
    now=now or datetime.now(timezone.utc)
    reasons=[]
    if not isinstance(t,dict) or set(t)-ALLOWED_KEYS:
        return ['INVALID_TICKET_SCHEMA']
    if t.get('news_first') is not True or t.get('event_verified') is not True or t.get('reaction_confirmed') is not True:
        reasons.append('NEWS_OR_REACTION_NOT_VERIFIED')
    if t.get('side')!='buy' or t.get('asset_class')!='us_equity':
        reasons.append('ONLY_LONG_US_EQUITY_PAPER_SUPPORTED')
    if not re.fullmatch(r'[A-Z]{1,5}',str(t.get('symbol',''))):
        reasons.append('INVALID_SYMBOL')
    if not str(t.get('event_id','')).strip() or not str(t.get('primary_source_url','')).startswith('https://'):
        reasons.append('MISSING_PRIMARY_EVIDENCE')
    try:
        event_time=parse_time(t['event_verified_at_utc'])
        quote_time=parse_time(t['price_observed_at_utc'])
        if not (now-timedelta(days=5)<=event_time<=quote_time<=now+timedelta(seconds=10)):
            reasons.append('EVENT_TIME_ORDER_OR_STALENESS')
        if now-quote_time>timedelta(seconds=60):
            reasons.append('STALE_PRICE')
        entry=amount(t['entry']);stop=amount(t['stop']);target=amount(t['target'])
        qty=t['quantity']
        if type(qty)!=int or qty<1 or qty>10000:
            reasons.append('INVALID_INTEGER_QUANTITY')
        elif not (entry>stop>0 and target>entry and target-entry>=2*(entry-stop)):
            reasons.append('INVALID_BRACKET_OR_REWARD')
        else:
            notional=qty*entry
            risk=qty*(entry-stop)
            if risk>Decimal('50')/fx or notional>Decimal('5000')/fx:
                reasons.append('CAPITAL_OR_ONE_PERCENT_RISK_EXCEEDED')
    except (KeyError,ValueError,TypeError):
        reasons.append('INVALID_NUMERIC_OR_TIME_FIELD')
    return reasons

def account_gate(account,positions,orders,t,fx):
    reasons=[]
    if account.get('status')!='ACTIVE' or account.get('currency')!='USD' or account.get('trading_blocked'):
        reasons.append('ACCOUNT_UNAVAILABLE')
    if orders:
        reasons.append('EXISTING_OPEN_ORDERS')
    if len(positions)>=3:
        reasons.append('MAX_POSITIONS')
    if any(x.get('symbol')==t['symbol'] for x in positions):
        reasons.append('DUPLICATE_SYMBOL_POSITION')
    if any(x.get('side')!='long' or amount(x.get('market_value',0))<0 for x in positions):
        reasons.append('EXISTING_SHORT_EXPOSURE')
    exposure=sum((abs(amount(x.get('market_value',0))) for x in positions),Decimal(0))
    requested=amount(t['entry'])*t['quantity']
    if exposure+requested>Decimal('5000')/fx:
        reasons.append('PORTFOLIO_CAPITAL_LIMIT')
    if amount(account.get('cash',0))<requested or amount(account.get('equity',0))<requested:
        reasons.append('CASH_ONLY_NO_MARGIN')
    return reasons

def order_body(t, fp):
    return {'symbol':t['symbol'],'qty':str(t['quantity']), 'side':'buy',
            'type':'limit','limit_price':str(t['entry']),'time_in_force':'day',
            'order_class':'bracket','take_profit':{'limit_price':str(t['target'])},
            'stop_loss':{'stop_price':str(t['stop'])}, 'client_order_id':'nf-'+fp}

def send_paper(body,env,opener=urlopen):
    req=Request(PAPER_URL+'/v2/orders',data=json.dumps(body).encode(),method='POST',
                headers={'APCA-API-KEY-ID':env['ALPACA_API_KEY'],
                         'APCA-API-SECRET-KEY':env['ALPACA_SECRET_KEY'],
                         'Content-Type':'application/json'})
    with opener(req,timeout=15) as response:
        return json.load(response)

def process(t,env,confirm=None,opener=urlopen,now=None,log=LOG):
    fx=validate_env(env)
    reasons=ticket_gate(t,fx,now=now)
    fp=fingerprint(t)
    if reasons:
        return {'status':'BLOCKED','reasons':reasons,'fingerprint':fp,'orders_sent':0}
    if env.get('PAPER_EXECUTION_ENABLED','false').lower()!='true':
        return {'status':'PREVIEW_ONLY','reason':'PAPER_EXECUTION_ENABLED_NOT_TRUE','fingerprint':fp,
                'order_preview':order_body(t,fp),'orders_sent':0}
    if confirm!=fp:
        return {'status':'AWAITING_ORDER_SPECIFIC_APPROVAL','fingerprint':fp,
                'order_preview':order_body(t,fp),'orders_sent':0}
    # Fetch and recheck live Paper account directly before submission.
    try:
        a=get_json('/v2/account',env,opener)
        p=get_json('/v2/positions',env,opener)
        o=get_json('/v2/orders?status=open&limit=500',env,opener)
        reasons=account_gate(a,p,o,t,fx)
        if reasons:
            return {'status':'BLOCKED','reasons':reasons,'fingerprint':fp,'orders_sent':0}
        if log.exists() and any(fp==json.loads(line).get('fingerprint') for line in log.read_text().splitlines() if line.strip()):
            return {'status':'BLOCKED','reasons':['ORDER_ALREADY_SUBMITTED'],'orders_sent':0}
        log.parent.mkdir(parents=True,exist_ok=True)
        response=send_paper(order_body(t,fp),env,opener)
        record={'fingerprint':fp,'at':datetime.now(timezone.utc).isoformat(),
                'broker_id':response.get('id'),'client_order_id':'nf-'+fp,'status':response.get('status')}
        with log.open('a') as handle:handle.write(json.dumps(record)+'\n')
        return {'status':'PAPER_SUBMITTED','broker_id':response.get('id'),'fingerprint':fp,
                'orders_sent':1,'broker_status':response.get('status')}
    except Exception as exc:
        # A timed out POST may have been accepted. Never automatically retry it.
        return {'status':'UNKNOWN_BROKER_STATE_DO_NOT_RETRY','error_type':type(exc).__name__,
                'client_order_id':'nf-'+fp,'orders_sent':'UNKNOWN'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ticket',required=True)
    parser.add_argument('--confirm-fingerprint',default=None)
    args=parser.parse_args()
    if os.environ.get('LIVE_TRADING_ENABLED','false').lower()!='false':
        print(json.dumps({'status':'BLOCKED_LIVE_FLAG','orders_sent':0}));return 2
    try:
        t=json.loads(Path(args.ticket).read_text())
        result=process(t,os.environ,args.confirm_fingerprint)
    except Exception as exc:
        result={'status':'BLOCKED','error_type':type(exc).__name__,'orders_sent':0}
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result['status'] in ('PREVIEW_ONLY','AWAITING_ORDER_SPECIFIC_APPROVAL','PAPER_SUBMITTED') else 2

if __name__=='__main__':sys.exit(main())
