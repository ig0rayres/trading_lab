"""Process authenticated queued TradingView signals using existing Paper runner."""
import argparse
import fcntl
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from signal_paper_runner import run
from signal_copy import validate
from paper_audit import validate_env

BASE=Path(os.environ.get('TV_QUEUE_DIR','/app/reports/webhooks/pending'))

def process_one(path):
    # Atomic rename before processing, prevents double-run from concurrent workers.
    processing=BASE.parent/'processing';processing.mkdir(parents=True,exist_ok=True)
    claimed=processing/path.name
    try:path.rename(claimed)
    except FileNotFoundError:return None
    try:
        obj=json.loads(claimed.read_text())
        fx=validate_env(os.environ)
        errs=validate(obj,os.environ.get('SIGNAL_COPY_SECRET',''),fx)
        result={'status':'BLOCKED','reasons':errs,'orders_sent':0} if errs else run(obj,os.environ)
    except Exception as e:
        result={'status':'BLOCKED','reasons':[type(e).__name__],'orders_sent':0}
    completed=BASE.parent/'processed';completed.mkdir(parents=True,exist_ok=True)
    archive=completed/path.name
    claimed.rename(archive)
    with (BASE.parent/'journal.jsonl').open('a') as f:
        f.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(), 'file_id':path.stem,'result':result},ensure_ascii=False)+'\n')
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--once',action='store_true');a=p.parse_args()
    BASE.mkdir(parents=True,exist_ok=True)
    lock=BASE.parent/'worker.lock'
    with lock.open('a+') as f:
        fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        results=[]
        for path in sorted(BASE.glob('*.json')):
            results.append(process_one(path))
        print(json.dumps({'processed':len(results),'outcomes':results,'live_trading':False},ensure_ascii=False))
if __name__=='__main__':main()
