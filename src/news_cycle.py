"""Read-only, dual-market News First run, reusing existing audit/catalog/triage/journal.

All data comes from existing Alpaca GET news audit; never sends orders or
constructs prices, stops, confirmations, or P&L from headlines.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT = {'stocks': 'AAPL,MSFT,NVDA,AMD,TSLA,PLTR', 'crypto': 'BTCUSD,ETHUSD'}


def window(days, now=None):
    now = now or datetime.now(timezone.utc)
    if not 1 <= days <= 14:
        raise ValueError('days must be in 1..14')
    return (now - timedelta(days=days)).date().isoformat(), (now + timedelta(days=1)).date().isoformat()


def execute(market, symbols, start, end, pages, base, runner=None):
    if market not in DEFAULT:
        raise ValueError('Unsupported market')
    root = (Path(base) / market)
    root.mkdir(parents=True, exist_ok=True)
    steps = [
        ('news_audit.py', ['--start', start, '--end', end, '--symbols', symbols,
                           '--pages', str(pages), '--output', str(root/'coverage.json')]),
        ('news_catalog.py', ['--input', str(root/'coverage.json'), '--output', str(root/'catalog.json')]),
        ('event_verifier.py', ['--input', str(root/'catalog.json'), '--output', str(root/'evidence-triage.json')]),
        ('news_first_sim.py', ['--input', str(root/'evidence-triage.json'),
                               '--output', str(root/'simulation-signals.json'),
                               '--journal', str(root/'simulation-journal.jsonl')]),
    ]
    runner = runner or subprocess.run
    for script, args in steps:
        cmd = [sys.executable, str(ROOT/script), *args]
        r = runner(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode:
            return {'market': market, 'health': 'BLOCKED', 'failed_step': script,
                    'detail': (r.stdout + r.stderr)[-800:], 'orders_sent': 0}
    report = json.loads((root/'simulation-signals.json').read_text(encoding='utf-8'))
    return {'market': market, 'health': report.get('health'), 'symbols': symbols.split(','),
            **report['summary'], 'orders_sent': 0, 'report': str(root/'simulation-signals.json')}


def main():
    parser = argparse.ArgumentParser(description='Dual-market read-only News First cycle')
    parser.add_argument('--days', type=int, default=3)
    parser.add_argument('--pages', type=int, default=20)
    parser.add_argument('--stocks', default=DEFAULT['stocks'])
    parser.add_argument('--crypto', default=DEFAULT['crypto'])
    parser.add_argument('--base', default='/app/reports/news/cycle')
    args = parser.parse_args()
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        print(json.dumps({'health':'BLOCKED_LIVE_TRADING_FLAG', 'orders_sent':0}))
        return 2
    if not 1 <= args.pages <= 20:
        print(json.dumps({'health':'BLOCKED_INVALID_PAGES', 'orders_sent':0}))
        return 2
    try:
        start, end = window(args.days)
        outputs = [execute(m, symbols, start, end, args.pages, args.base)
                   for m, symbols in [('stocks',args.stocks),('crypto',args.crypto)]]
        out = {'mode':'NEWS_FIRST_DUAL_MARKET_READ_ONLY','health':'OK_RESEARCH_ONLY' if all(x['health']=='OK_RESEARCH_ONLY' for x in outputs) else 'PARTIAL_OR_BLOCKED',
               'start':start,'end':end,'markets':outputs,'orders_sent':0,
               'authorized_to_trade':False,
               'warning':'No price execution or P&L simulator; unverified news does not constitute a trade.'}
        folder=Path(args.base); folder.mkdir(parents=True,exist_ok=True)
        (folder/'latest.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
        print(json.dumps(out,ensure_ascii=False))
        return 0 if out['health']=='OK_RESEARCH_ONLY' else 2
    except (ValueError,OSError,subprocess.TimeoutExpired) as e:
        print(json.dumps({'health':'BLOCKED','error':str(e),'orders_sent':0}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
