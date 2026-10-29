"""Fail-closed research orchestration. Never contacts order endpoints.

Cycles existing scanners, news pipeline and dashboard. Outcomes are persisted for
operators; a partial failure cannot be mistaken for deployment readiness.
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def cycle(reports, opportunity_input=None, news=False, runner=None, now=None):
    if os.environ.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        raise ValueError('LIVE_TRADING_NOT_DISABLED')
    reports = Path(reports)
    reports.mkdir(parents=True, exist_ok=True)
    runner = runner or subprocess.run
    run_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
    jobs = []
    if opportunity_input:
        jobs.append(('opportunity_scan', 'market_opportunities.py', ['--input', str(opportunity_input), '--output', str(reports/'research'/'opportunities-latest.json')]))
    if news:
        jobs.append(('news_first', 'news_cycle.py', ['--base', str(reports/'news'/'cycle')]))
    jobs.append(('dashboard', 'trading_dashboard_data.py', ['--root', str(reports), '--output', str(reports/'dashboard'/'latest.json')]))
    outcomes = []
    for name, module, args in jobs:
        cmd = [sys.executable, str(ROOT/module), *args]
        try:
            p = runner(cmd, capture_output=True, text=True, timeout=300)
            status = 'OK' if p.returncode == 0 else 'BLOCKED'
            detail = (p.stderr or p.stdout)[-400:] if p.returncode else None
        except (OSError, subprocess.TimeoutExpired) as exc:
            status, detail = 'BLOCKED', type(exc).__name__
        outcomes.append({'job': name, 'status': status, 'detail': detail})
    result = {'schema_version':'v4-cycle-1', 'at_utc':run_at, 'mode':'RESEARCH_ONLY',
              'status':'OK_RESEARCH_ONLY' if all(x['status']=='OK' for x in outcomes) else 'PARTIAL_OR_BLOCKED',
              'jobs':outcomes, 'paper_approved':False, 'orders_sent':0,
              'limitations':['No autonomous signal promotion', 'No broker order submission', 'B3 and crypto execution not enabled']}
    dst = reports/'research'/'v4-cycle-latest.json'
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    tmp.replace(dst)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--reports', default='/app/reports')
    p.add_argument('--opportunity-input')
    p.add_argument('--news', action='store_true', help='Use existing Alpaca GET news ingestion; needs data credentials')
    a=p.parse_args()
    try:
        result=cycle(a.reports, a.opportunity_input, a.news)
    except (ValueError, OSError) as exc:
        print(json.dumps({'status':'BLOCKED','reason':str(exc),'orders_sent':0}));return 2
    print(json.dumps(result,ensure_ascii=False));return 0 if result['status']=='OK_RESEARCH_ONLY' else 2


if __name__=='__main__':raise SystemExit(main())
