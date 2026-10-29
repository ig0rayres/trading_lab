"""Read-only news-first decision ledger. No broker import, orders, or live data calls.

Produces preliminary review signals and an idempotent decision journal. Never
creates an actionable trade from unverified headline metadata.
"""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def make_report(triage):
    if triage.get('mode') != 'NEWS_EVENT_EVIDENCE_TRIAGE_READ_ONLY' or triage.get('health') != 'OK_UNVERIFIED_REVIEW_QUEUE':
        raise ValueError('Evidence triage missing or unhealthy')
    if not isinstance(triage.get('review_queue'), list):
        raise ValueError('Missing review queue')
    candidates = []
    for e in triage['review_queue']:
        sym = sorted(set(e.get('tracked_symbols') or []))
        if not sym:
            continue
        for s in sym:
            uid = hashlib.sha256(f"{e.get('article_id')}|{s}|NEWS_FIRST".encode()).hexdigest()[:20]
            reasons = ['PRIMARY_SOURCE_NOT_INDEPENDENTLY_VERIFIED', 'EVENT_SURPRISE_NOT_VERIFIED',
                       'FIRST_TRADABLE_AVAILABILITY_NOT_VERIFIED', 'MARKET_REACTION_NOT_EVALUATED',
                       'ORDER_RISK_GATES_NOT_VERIFIED']
            if s not in e.get('direct_issuer_mentions', []):
                reasons.insert(0, 'ISSUER_NOT_CONFIRMED_DIRECT')
            candidates.append(dict(id=uid, article_id=e.get('article_id'), symbol=s,
                                   headline=e.get('headline'), observed_news_timestamp=e.get('provider_created_at_utc'),
                                   source_url=e.get('source_url'), relation=e.get('relation'),
                                   event_types=e.get('candidate_types', []), side='UNDETERMINED',
                                   decision='NO_TRADE', research_status='EVIDENCE_PENDING',
                                   entry=None, stop=None, target=None, quantity=0,
                                   blocker_reasons=reasons))
    candidates.sort(key=lambda e: (str(e['observed_news_timestamp']), e['symbol'],e['id']))
    return dict(mode='NEWS_FIRST_INTERNAL_SIMULATION', health='OK_RESEARCH_ONLY',
                generated_at_utc=datetime.now(timezone.utc).isoformat(),
                signals=candidates, summary={'review_signals':len(candidates), 'actionable_signals':0,
                'simulated_positions_opened':0, 'no_trade':len(candidates)},
                orders_sent=0, authorized_to_trade=False,
                limitations=['No source verification or price reaction has been performed.',
                             'All signals remain NO_TRADE until evidence and causally-timed pricing are supplied.',
                             'Journal records decisions, not executed orders or P&L.',
                             'Review signals may refer to overlapping news events.'])


def persist(report, report_path, journal_path):
    a = Path(report_path); b = Path(journal_path)
    if a.resolve() == b.resolve():
        raise ValueError('Report and journal files must differ')
    a.parent.mkdir(parents=True, exist_ok=True); b.parent.mkdir(parents=True, exist_ok=True)
    # Prevent pre-existing symlinks from being followed.
    if a.is_symlink() or b.is_symlink():
        raise ValueError('Symlink output not allowed')
    previous = []
    if b.exists():
        previous = [json.loads(line) for line in b.read_text(encoding='utf-8').splitlines() if line.strip()]
    seen = {x['id'] for x in previous}
    new = []
    for signal in report['signals']:
        if signal['id'] not in seen:
            new.append({'id':signal['id'], 'article_id':signal['article_id'],
                        'symbol':signal['symbol'], 'news_time':signal['observed_news_timestamp'],
                        'recorded_at_utc':report['generated_at_utc'], 'decision':'NO_TRADE',
                        'status':'EVIDENCE_PENDING', 'orders_sent':0, 'blockers':signal['blocker_reasons']})
            seen.add(signal['id'])
    a.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    if new:
        with b.open('a',encoding='utf-8') as f:
            for x in new:
                f.write(json.dumps(x,ensure_ascii=False)+'\n')
    return len(new)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input', default='/app/reports/news/evidence-triage.json')
    p.add_argument('--output', default='/app/reports/news/simulation-signals.json')
    p.add_argument('--journal', default='/app/reports/news/simulation-journal.jsonl')
    args=p.parse_args()
    try:
        report=make_report(json.loads(Path(args.input).read_text(encoding='utf-8')))
        added=persist(report,args.output,args.journal)
        print(json.dumps({'health':report['health'], **report['summary'], 'new_journal_records':added,
                          'orders_sent':0,'authorized_to_trade':False,
                          'report':args.output,'journal':args.journal}))
        return 0
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as e:
        print(json.dumps({'health':'BLOCKED_INPUT','error':type(e).__name__,'message':str(e),
                          'orders_sent':0,'authorized_to_trade':False}))
        return 2

if __name__=='__main__':
    raise SystemExit(main())
