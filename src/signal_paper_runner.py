"""One-shot signed external-signal Alpaca PAPER runner. Fail closed, never live.

No strategy validation, only authentication, price freshness, allocation and risk.
No autonomous scheduler/webhook listener is bundled. Run this against actual
signed signal JSON; approved mode only with explicit PAPER_SIGNAL_AUTO_ENABLED.
"""
import argparse
import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from paper_audit import PAPER_URL, get_json, validate_env, amount
from signal_copy import validate, canonical_payload
from portfolio_risk_v4 import evaluate as evaluate_portfolio_risk

DEFAULT_LEDGER = '/app/reports/paper/signal-orders.jsonl'


def token(signal):
    return hashlib.sha256(canonical_payload(signal)).hexdigest()[:24]


def risk_check(signal, account, positions, open_orders, fx, env):
    reasons=[]
    cap=Decimal('10000')/fx
    per_trade=Decimal('20' if signal.get('provider') in set(filter(None,env.get('PRODIGY_PROVIDERS','').split(','))) else '50')/fx
    try:
        entry, stop, target = (amount(signal[k]) for k in ('entry','stop','target'))
        qty=signal['quantity']
        if type(qty)!=int or qty<1 or entry<=stop or stop<=0 or target<=entry:
            reasons.append('INVALID_TICKET')
        else:
            if qty*(entry-stop)>per_trade: reasons.append('TRADE_RISK_LIMIT')
            if qty*entry>cap: reasons.append('CAPITAL_LIMIT')
        if not isinstance(positions,list) or not isinstance(open_orders,list):
            return ['INVALID_BROKER_RESPONSE']
        if account.get('status')!='ACTIVE' or account.get('currency')!='USD' or account.get('trading_blocked'):
            reasons.append('ACCOUNT_NOT_ACTIVE')
        if len(positions)>=3: reasons.append('MAX_POSITIONS')
        if open_orders: reasons.append('OPEN_ORDERS_REQUIRE_REVIEW')
        if any(x.get('symbol')==signal['symbol'] for x in positions): reasons.append('DUPLICATE_SYMBOL')
        if any(x.get('side')!='long' for x in positions): reasons.append('SHORT_EXPOSURE')
        exposure=sum((abs(amount(x['market_value'])) for x in positions),Decimal(0))
        if exposure + entry*qty>cap: reasons.append('TOTAL_CAP_EXCEEDED')
        if amount(account.get('cash',0))<entry*qty: reasons.append('INSUFFICIENT_CASH')
        if amount(account.get('equity',0))<entry*qty: reasons.append('INSUFFICIENT_EQUITY')
        if account.get('pattern_day_trader') and amount(account.get('equity',0))<Decimal('25000'):
            reasons.append('PDT_ACCOUNT_REVIEW')
        # Do not claim consolidated daily loss enforcement without verified P&L.
        if env.get('PAPER_DAILY_RISK_CONFIRMED','false').lower()!='true':
            reasons.append('DAILY_RISK_NOT_CONFIRMED')
        # A separate, fresh, externally reconciled multi-market snapshot is mandatory.
        # The Alpaca positions endpoint alone cannot establish B3/crypto exposure.
        # Never infer verified P&L from an environment boolean.
        from datetime import timedelta
        snapshot_file = env.get('V4_RISK_SNAPSHOT_FILE', '')
        if not snapshot_file:
            reasons.append('V4_PORTFOLIO_SNAPSHOT_REQUIRED')
        else:
            try:
                snapshot = json.loads(Path(snapshot_file).read_text())
                stamp = datetime.fromisoformat(snapshot['at_utc'].replace('Z', '+00:00'))
                if stamp.tzinfo is None or abs((datetime.now(timezone.utc) - stamp).total_seconds()) > 120:
                    reasons.append('V4_PORTFOLIO_SNAPSHOT_STALE')
                # A snapshot must be anchored to the currently observed US broker state.
                if snapshot.get('alpaca_positions_count') != len(positions) or snapshot.get('alpaca_open_orders_count') != len(open_orders):
                    reasons.append('V4_BROKER_SNAPSHOT_MISMATCH')
                candidate = {'market':'US_EQUITY', 'symbol':signal['symbol'], 'side':'buy',
                             'verified':True, 'trading_mode':'PAPER', 'quantity':qty,
                             'entry_brl':str(entry*fx), 'stop_brl':str(stop*fx),
                             'prodigy':signal.get('provider') in set(filter(None,env.get('PRODIGY_PROVIDERS','').split(',')))}
                assessment = evaluate_portfolio_risk(candidate, snapshot)
                reasons.extend(assessment['reasons'])
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                reasons.append('V4_PORTFOLIO_SNAPSHOT_INVALID')
    except (ValueError, TypeError, KeyError):
        reasons.append('INVALID_ACCOUNT_OR_SIGNAL')
    return reasons


def make_order(signal, fp):
    return {'symbol':signal['symbol'],'qty':str(signal['quantity']),
            'side':'buy','type':'limit','limit_price':str(signal['entry']),
            'time_in_force':'day','order_class':'bracket',
            'take_profit':{'limit_price':str(signal['target'])},
            'stop_loss':{'stop_price':str(signal['stop'])},
            'client_order_id':'nf-'+fp}


def submit(body,env,opener=urlopen):
    req=Request(PAPER_URL+'/v2/orders',data=json.dumps(body).encode(),method='POST',
        headers={'APCA-API-KEY-ID':env['ALPACA_API_KEY'],
                 'APCA-API-SECRET-KEY':env['ALPACA_SECRET_KEY'],
                 'Content-Type':'application/json'})
    with opener(req, timeout=15) as r: return json.load(r)


def run(signal,env,ledger=DEFAULT_LEDGER,broker_get=get_json,broker_post=submit,now=None):
    now=now or datetime.now(timezone.utc)
    try:
        fx=validate_env(env)
        errors=validate(signal,env.get('SIGNAL_COPY_SECRET',''),fx,now=now)
        if errors: return {'status':'BLOCKED','reasons':errors,'orders_sent':0}
        # signal_copy has old 5k/50 risk: do not loosen its acceptance silently.
        fp=token(signal)
        body=make_order(signal,fp)
        if env.get('PAPER_SIGNAL_AUTO_ENABLED','false').lower()!='true':
            return {'status':'PREVIEW_ONLY','client_order_id':'nf-'+fp,'order_preview':body,'orders_sent':0}
        if env.get('PAPER_EXECUTION_ENABLED','false').lower()!='true':
            return {'status':'BLOCKED','reasons':['PAPER_EXECUTION_NOT_ENABLED'],'orders_sent':0}
        if env.get('PAPER_SIGNAL_ACCOUNT_ACK','')!='I_AUTHORIZE_ALPACA_PAPER_ONLY':
            return {'status':'BLOCKED','reasons':['EXPLICIT_PAPER_ACK_REQUIRED'],'orders_sent':0}
        path=Path(ledger);path.parent.mkdir(parents=True,exist_ok=True)
        with (path.parent/'signal-orders.lock').open('a+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            past=[]
            if path.exists():
                for line in path.read_text().splitlines():
                    if line.strip(): past.append(json.loads(line))
            if any(x.get('client_order_id')=='nf-'+fp for x in past):
                return {'status':'BLOCKED','reasons':['ALREADY_ATTEMPTED_RECONCILE_FIRST'],'orders_sent':0}
            a=broker_get('/v2/account',env)
            pos=broker_get('/v2/positions',env)
            orders=broker_get('/v2/orders?status=open&limit=500',env)
            reasons=risk_check(signal,a,pos,orders,fx,env)
            if reasons: return {'status':'BLOCKED','reasons':reasons,'orders_sent':0}
            # Commit intent BEFORE POST; ambiguous network failures must not double-submit.
            record={'at':now.isoformat(),'client_order_id':'nf-'+fp,'provider':signal['provider'],
                    'signal_id':signal['signal_id'],'state':'ATTEMPTED_UNKNOWN'}
            with path.open('a') as f:
                f.write(json.dumps(record)+'\n');f.flush();os.fsync(f.fileno())
            try:
                response=broker_post(body,env)
                with path.open('a') as f:
                    f.write(json.dumps({**record,'state':'SUBMITTED','broker_id':response.get('id'),
                                         'broker_status':response.get('status')})+'\n')
                    f.flush();os.fsync(f.fileno())
                return {'status':'PAPER_SUBMITTED','client_order_id':'nf-'+fp,
                        'broker_id':response.get('id'),'broker_status':response.get('status'),'orders_sent':1}
            except Exception as exc:
                return {'status':'UNKNOWN_DO_NOT_RETRY','client_order_id':'nf-'+fp,
                        'error_type':type(exc).__name__,'orders_sent':'UNKNOWN'}
    except Exception as exc:
        return {'status':'BLOCKED','reasons':[type(exc).__name__],'orders_sent':0}


def main():
    p=argparse.ArgumentParser(description='Signed signal to Alpaca PAPER; preview by default')
    p.add_argument('--signal',required=True)
    args=p.parse_args()
    result=run(json.loads(Path(args.signal).read_text()),os.environ)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0 if result['status'] in ('PREVIEW_ONLY','PAPER_SUBMITTED') else 2

if __name__=='__main__': raise SystemExit(main())
