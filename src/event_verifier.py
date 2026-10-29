"""Read-only evidence triage. Never equate headline or supplied claims with verification."""
import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ISSUERS = {'AAPL': ('apple',), 'MSFT': ('microsoft',), 'NVDA': ('nvidia',)}
KEYWORDS = {'EARNINGS': ('earnings', 'revenue', 'eps', 'profit'),
            'GUIDANCE': ('outlook', 'guidance'),
            'CORPORATE_ACTION': ('acquire', 'acquires', 'acquisition', 'buys', 'merger'),
            'REGULATORY': ('lawsuit', 'antitrust', 'regulatory', 'court')}

def assess(event):
    headline = str(event.get('headline') or '')
    tags = list(event.get('candidate_types') or [])
    mentioned = list(event.get('requested_symbols_mentioned') or [])
    issuer_matches = [s for s in mentioned if any(re.search(r'\b' + re.escape(n) + r"(?:'s)?\b", headline, re.I) for n in ISSUERS.get(s, ()))]
    if not issuer_matches:
        relation = 'INDIRECT_OR_UNKNOWN'
    elif len(issuer_matches) == 1:
        relation = 'DIRECT_MENTION_NEEDS_REVIEW'
    else:
        relation = 'MULTIPLE_DIRECT_MENTIONS_NEEDS_REVIEW'
    # Earnings of a named third party must never be assigned to the tracked symbol.
    if 'EARNINGS' in tags and not issuer_matches:
        relation = 'EARNINGS_NOT_ATTRIBUTABLE_TO_TRACKED_ISSUER'
    return {'article_id': event.get('article_id'), 'headline': headline,
            'provider_created_at_utc': event.get('provider_created_at_utc'),
            'source_url': event.get('source_url'), 'tracked_symbols': mentioned,
            'candidate_types': tags, 'direct_issuer_mentions': issuer_matches,
            'relation': relation, 'event_status': 'UNVERIFIED',
            'primary_source_verified': False, 'surprise_verified': False,
            'first_tradable_availability_verified': False, 'direction': 'UNKNOWN',
            'strategy_eligible': False}

def build_report(catalog):
    if catalog.get('mode') != 'NEWS_EVENT_CATALOG_READ_ONLY' or catalog.get('health') != 'OK_UNVERIFIED_LEADS':
        raise ValueError('Expected complete news-catalog report')
    if not isinstance(catalog.get('events'), list):
        raise ValueError('Missing events list')
    leads = [assess(e) for e in catalog['events'] if e.get('candidate_types')]
    # Keep each article separate until independent evidence establishes equivalence.
    # Suggestions never merge event records or increase verification counters.
    suggestions = []
    for i, a in enumerate(leads):
        for b in leads[i+1:]:
            if not set(a['tracked_symbols']).intersection(b['tracked_symbols']):
                continue
            if not set(a['candidate_types']).intersection(b['candidate_types']):
                continue
            aw = set(re.findall(r'[a-z]{5,}', a['headline'].lower()))
            bw = set(re.findall(r'[a-z]{5,}', b['headline'].lower()))
            common = aw & bw - {'their', 'would', 'after', 'about', 'company', 'market', 'shares', 'stock', 'report'}
            if len(common) >= 3:
                suggestions.append({'article_ids': [a['article_id'], b['article_id']],
                                    'reason': 'headline_keyword_overlap', 'common_words': sorted(common)[:12],
                                    'status': 'DUPLICATE_SUGGESTION_UNVERIFIED'})
    counts = Counter(x['relation'] for x in leads)
    return {'mode': 'NEWS_EVENT_EVIDENCE_TRIAGE_READ_ONLY', 'health': 'OK_UNVERIFIED_REVIEW_QUEUE',
            'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'audit_interval': catalog.get('audit_interval'), 'requested_symbols': catalog.get('requested_symbols'),
            'summary': {'candidate_articles': len(leads), 'relation_counts': dict(counts),
                        'possible_duplicate_pairs': len(suggestions), 'verified_events': 0,
                        'strategy_eligible_events': 0},
            'review_queue': leads, 'duplicate_suggestions': suggestions,
            'verification_requirements': ['official_primary_source_url', 'issuer_of_event',
                'event_type', 'official_release_time_utc', 'first_accessible_time_evidence',
                'original_analyst_consensus_timestamp_if_earnings', 'reviewer_evidence'],
            'limitations': ['Direct mention detection uses heuristics and is not proof of materiality.',
                            'Duplicate suggestions do not automatically merge articles.',
                            'News creation time is not first tradable availability.',
                            'No primary-source browsing or independent validation is performed.',
                            'All candidates remain UNVERIFIED and ineligible for trading.'],
            'strategy_eligible': False, 'orders_sent': 0, 'authorized_to_trade': False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='/app/reports/news/catalog.json')
    p.add_argument('--output', default='/app/reports/news/evidence-triage.json')
    args = p.parse_args()
    try:
        if Path(args.input).resolve() == Path(args.output).resolve():
            raise ValueError('Input and output must differ')
        result = build_report(json.loads(Path(args.input).read_text(encoding='utf-8')))
        exit_code = 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        result = {'mode': 'NEWS_EVENT_EVIDENCE_TRIAGE_READ_ONLY', 'health': 'BLOCKED_INPUT',
                  'error': type(exc).__name__, 'strategy_eligible': False,
                  'orders_sent': 0, 'authorized_to_trade': False}
        exit_code = 2
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('review_queue','duplicate_suggestions','limitations','verification_requirements')}, ensure_ascii=False))
    return exit_code

if __name__ == '__main__':
    raise SystemExit(main())
