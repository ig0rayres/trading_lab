"""TradingView HTTPS-terminated webhook ingress. Queue only, never orders in HTTP thread."""
import argparse
import hashlib
import hmac
import json
import os
import re
import tempfile
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

QUEUE=Path(os.environ.get('TV_QUEUE_DIR','/app/reports/webhooks/pending'))
FIELDS={'provider','signal_id','symbol','side','asset_class','sent_at_utc','entry','stop','target','quantity','ttl_seconds'}
_ENTRY = None

def _entry_module():
    global _ENTRY
    if _ENTRY is None:
        from original import load_original
        _ENTRY = load_original().entry
    return _ENTRY

def _within_regular_session(now):
    from zoneinfo import ZoneInfo
    ny = now.astimezone(ZoneInfo('America/New_York'))
    sess = _entry_module().session(ny.date())
    if sess is None:
        return False
    open_t, close_t = sess
    t = ny.time()
    return open_t <= t <= close_t

def _respond(payload, status, body):
    from gate_a_signal import maybe_persist
    maybe_persist(payload if isinstance(payload, dict) else {}, status, body)
    return status, body

def ingest(payload,secret,queue=QUEUE,now=None):
    now=now or datetime.now(timezone.utc)
    if not isinstance(payload,dict) or set(payload)!=FIELDS:
        return _respond({},422,{'status':'REJECTED','reason':'INVALID_FIELDS'})
    if payload['provider']!='tradingview':
        return _respond(payload,422,{'status':'REJECTED','reason':'INVALID_PROVIDER'})
    if not re.fullmatch(r'[A-Za-z0-9_.:-]{6,100}',str(payload['signal_id'])):
        return _respond(payload,422,{'status':'REJECTED','reason':'INVALID_SIGNAL_ID'})
    if payload.get('side')!='buy' or payload.get('asset_class')!='us_equity':
        return _respond(payload,422,{'status':'REJECTED','reason':'UNSUPPORTED_ASSET_OR_SIDE'})
    if not _within_regular_session(now):
        return _respond(payload,422,{'status':'REJECTED','reason':'OUTSIDE_SESSION'})
    try:
        ts=datetime.fromisoformat(payload['sent_at_utc'].replace('Z','+00:00'))
        if ts.tzinfo is None:raise ValueError()
        delta=(now-ts.astimezone(timezone.utc)).total_seconds()
        ttl=payload['ttl_seconds']
        if type(ttl)!=int or not 1<=ttl<=60 or not -5<=delta<=ttl:raise ValueError()
    except (TypeError,ValueError,AttributeError):
        return _respond(payload,422,{'status':'REJECTED','reason':'STALE_OR_INVALID_TIMESTAMP'})
    # No need to store the URL token; HMAC is signed inside the trusted service.
    digest=hashlib.sha256((payload['provider']+'|'+payload['signal_id']).encode()).hexdigest()
    queue.mkdir(parents=True,exist_ok=True)
    dest=queue/(digest+'.json')
    if dest.exists() or (queue.parent/'processed'/dest.name).exists():
        return _respond(payload,200,{'status':'DUPLICATE_IGNORED','reference':digest[:16]})
    from signal_copy import sign
    signed=dict(payload)
    signed['signal_id']=hashlib.sha256(payload['signal_id'].encode()).hexdigest()[:32]
    signed['provider_signature']=sign(signed,os.environ.get('SIGNAL_COPY_SECRET',''))
    with tempfile.NamedTemporaryFile('w',dir=queue,delete=False,prefix='.tmp-',encoding='utf-8') as f:
        json.dump(signed,f,separators=(',',':'))
        tmp=Path(f.name)
    # Exclusive creation means duplicate submissions do not replace pending contents.
    try:
        import os as _os
        _os.link(tmp,dest)
    except FileExistsError:
        return _respond(payload,200,{'status':'DUPLICATE_IGNORED','reference':digest[:16]})
    finally:
        tmp.unlink(missing_ok=True)
    return _respond(payload,202,{'status':'QUEUED','reference':digest[:16],'orders_sent':0})

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass # do not log path token
    def do_GET(self):
        if self.path!='/health':self.send_error(404);return
        self.reply(200,{'status':'UP','mode':'PAPER_GATEWAY_QUEUE_ONLY'})
    def reply(self,status,obj):
        body=json.dumps(obj).encode();self.send_response(status)
        self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)))
        self.end_headers();self.wfile.write(body)
    def do_POST(self):
        secret=os.getenv('TV_WEBHOOK_TOKEN','')
        supplied=urlsplit(self.path).path.removeprefix('/webhook/')
        if not secret or len(secret)<32 or not hmac.compare_digest(supplied,secret):
            self.reply(404,{'status':'NOT_FOUND'});return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=8192 or 'application/json' not in self.headers.get('Content-Type',''):
                self.reply(415,{'status':'REJECTED','reason':'INVALID_BODY'});return
            payload=json.loads(self.rfile.read(length))
            status,result=ingest(payload,secret)
            self.reply(status,result)
        except (ValueError,TypeError,UnicodeError,json.JSONDecodeError):
            self.reply(400,{'status':'REJECTED','reason':'MALFORMED_JSON'})

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8080);a=p.parse_args()
    if os.getenv('LIVE_TRADING_ENABLED','false').lower()!='false':raise SystemExit('LIVE forbidden')
    if len(os.getenv('TV_WEBHOOK_TOKEN',''))<32 or len(os.getenv('SIGNAL_COPY_SECRET',''))<24:
        raise SystemExit('Set TV_WEBHOOK_TOKEN>=32 and SIGNAL_COPY_SECRET>=24')
    ThreadingHTTPServer(('0.0.0.0',a.port),Handler).serve_forever()
if __name__=='__main__':main()
