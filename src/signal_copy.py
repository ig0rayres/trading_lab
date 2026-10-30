"""External signal adapter: deterministic risk-only preflight, never sends orders.

Use it as a webhook JSON normalization boundary. Do not confuse it with an
execution service: no broker credentials, no network calls, no order submission.
"""
import argparse
import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from paper_audit import amount

ALLOWED = {'provider','signal_id','symbol','side','asset_class','sent_at_utc','entry',
           'stop','target','quantity','ttl_seconds','provider_signature','strategy_key'}
DEFAULT_MAX_AGE=30

def canonical_payload(signal):
    return json.dumps({k:v for k,v in signal.items() if k!='provider_signature'},sort_keys=True,separators=(',',':')).encode()

def sign(signal, secret):
    return hmac.new(secret.encode(), canonical_payload(signal),hashlib.sha256).hexdigest()

def validate(signal,secret,fx,now=None):
    now=now or datetime.now(timezone.utc)
    errors=[]
    if not isinstance(signal,dict) or set(signal)-ALLOWED:
        return ['INVALID_SCHEMA']
    if not secret or len(secret)<24 or not hmac.compare_digest(str(signal.get('provider_signature','')), sign(signal,secret)):
        errors.append('AUTH_FAILED')
    if not re.fullmatch(r'[a-zA-Z0-9_-]{2,40}',str(signal.get('provider',''))):
        errors.append('INVALID_PROVIDER')
    if not re.fullmatch(r'[a-zA-Z0-9_-]{6,100}',str(signal.get('signal_id',''))):
        errors.append('INVALID_SIGNAL_ID')
    if not re.fullmatch(r'[A-Z]{1,5}',str(signal.get('symbol',''))):
        errors.append('INVALID_SYMBOL')
    if signal.get('side')!='buy' or signal.get('asset_class')!='us_equity':
        errors.append('LONG_US_EQUITY_ONLY')
    try:
        ts=datetime.fromisoformat(str(signal['sent_at_utc']).replace('Z','+00:00'))
        if ts.tzinfo is None: raise ValueError('timezone missing')
        age=(now-ts.astimezone(timezone.utc)).total_seconds()
        ttl=int(signal.get('ttl_seconds',DEFAULT_MAX_AGE))
        if ttl<1 or ttl>60 or age < -5 or age>ttl: errors.append('EXPIRED_OR_FUTURE_SIGNAL')
    except (KeyError,TypeError,ValueError): errors.append('INVALID_TIMESTAMP_OR_TTL')
    try:
        entry,stop,target=(amount(signal[x]) for x in ('entry','stop','target'))
        qty=signal['quantity']
        if type(qty)!=int or qty<1: errors.append('INVALID_QUANTITY')
        elif not (entry>stop>0 and target>entry): errors.append('INVALID_PRICES')
        elif qty*(entry-stop)>Decimal('50')/fx or qty*entry>Decimal('5000')/fx:
            errors.append('RISK_OR_NOTIONAL_LIMIT')
    except (KeyError,TypeError,ValueError): errors.append('INVALID_PRICE_OR_QTY')
    return errors

def preflight(signal,secret,fx,now=None):
    errors=validate(signal,secret,fx,now)
    ref=hashlib.sha256(canonical_payload(signal) if isinstance(signal,dict) else b'invalid').hexdigest()[:24]
    if errors:
        result={'status':'BLOCKED','reasons':errors,'fingerprint':ref,'orders_sent':0}
        from gate_a_signal import persist_signal_copy_preflight
        persist_signal_copy_preflight(signal, result)
        return result
    result={'status':'SIGNAL_ACCEPTED_RISK_PREVIEW','fingerprint':ref,
            'provider':signal['provider'],'signal_id':signal['signal_id'],
            'symbol':signal['symbol'],'side':'buy','entry':signal['entry'],
            'stop':signal['stop'],'target':signal['target'], 'quantity':signal['quantity'],
            'orders_sent':0,'next_step':'Independent broker account and current-price checks required before execution'}
    from gate_a_signal import persist_signal_copy_preflight
    persist_signal_copy_preflight(signal, result)
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--signal',required=True,help='Path to signed JSON signal')
    args=parser.parse_args()
    if os.environ.get('LIVE_TRADING_ENABLED','false').lower()!='false':
        raise SystemExit('LIVE trading disabled')
    try:
        fx=amount(os.environ['USD_BRL_REFERENCE'])
        if not 2<=fx<=12: raise ValueError('fx')
        result=preflight(json.loads(Path(args.signal).read_text()), os.environ.get('SIGNAL_COPY_SECRET',''),fx)
    except (KeyError,ValueError,OSError) as e:
        result={'status':'BLOCKED','reasons':[type(e).__name__],'orders_sent':0}
    print(json.dumps(result,indent=2))
    return 0 if result['status']=='SIGNAL_ACCEPTED_RISK_PREVIEW' else 2

if __name__=='__main__': raise SystemExit(main())
