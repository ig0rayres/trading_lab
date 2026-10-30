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

def _within_regular_session(now):
    from gate_b_session import within_regular_session
    return within_regular_session(now)

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

def _configured_webhook_token(env=None):
    env = env or os.environ
    token = env.get('TV_WEBHOOK_TOKEN', '').strip()
    legacy = env.get('TV_WEBHOOK_SECRET', '').strip()
    return token or legacy

def dispatch_post(path, headers, body_bytes, env=None, now=None, queue=None):
    """HTTP POST entry for tests and Handler. Returns (status_code, body_dict)."""
    env = env or os.environ
    configured = _configured_webhook_token(env)
    path_only = urlsplit(path).path
    hdrs = {k.lower(): v for k, v in (headers or {}).items()}
    use_spec = path_only == '/webhooks/tradingview'
    legacy = path_only.startswith('/webhook/') and not use_spec
    if not use_spec and not legacy:
        return 404, {'status': 'NOT_FOUND'}
    if not configured or len(configured) < 32:
        return (401, {'status': 'UNAUTHORIZED'}) if use_spec else (404, {'status': 'NOT_FOUND'})
    if use_spec:
        supplied = (hdrs.get('x-webhook-token') or '').strip()
        if not supplied or not hmac.compare_digest(supplied, configured):
            return 401, {'status': 'UNAUTHORIZED'}
    else:
        supplied = path_only.removeprefix('/webhook/')
        if not supplied or not hmac.compare_digest(supplied, configured):
            return 404, {'status': 'NOT_FOUND'}
    try:
        if not body_bytes or len(body_bytes) > 8192:
            return 415, {'status': 'REJECTED', 'reason': 'INVALID_BODY'}
        ctype = hdrs.get('content-type', '')
        if 'application/json' not in ctype:
            return 415, {'status': 'REJECTED', 'reason': 'INVALID_BODY'}
        payload = json.loads(body_bytes.decode('utf-8'))
        status, result = ingest(payload, configured, queue=queue or QUEUE, now=now)
        return status, result
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        return 400, {'status': 'REJECTED', 'reason': 'MALFORMED_JSON'}

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
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            length = 0
        body = self.rfile.read(length) if length else b''
        hdr = {k: v for k, v in self.headers.items()}
        status, result = dispatch_post(self.path, hdr, body)
        self.reply(status, result)

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8080);a=p.parse_args()
    if os.getenv('LIVE_TRADING_ENABLED','false').lower()!='false':raise SystemExit('LIVE forbidden')
    if len(_configured_webhook_token())<32 or len(os.getenv('SIGNAL_COPY_SECRET',''))<24:
        raise SystemExit('Set TV_WEBHOOK_TOKEN>=32 (or TV_WEBHOOK_SECRET) and SIGNAL_COPY_SECRET>=24')
    ThreadingHTTPServer(('0.0.0.0',a.port),Handler).serve_forever()
if __name__=='__main__':main()
