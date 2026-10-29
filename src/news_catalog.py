"""Conservative, read-only catalog of potential catalysts from a news-audit JSON.

Headline tags are leads, never verified financial facts or trade signals.
"""
import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PATTERNS = (
    ('EARNINGS', r'\b(?:earnings|quarterly results|q[1-4] results|eps|quarterly profit|quarterly revenue|beats? estimates|misses? estimates)\b'),
    ('GUIDANCE', r'\b(?:guidance|outlook|forecast|raises? (?:full.year|annual) outlook|cuts? outlook)\b'),
    ('REGULATORY', r'\b(?:sec filing|fda approval|fda rejects?|antitrust|regulatory approval|investigation|lawsuit)\b'),
    ('CORPORATE_ACTION', r'\b(?:acquisition|acquires?|merger|takeover|buyout|spinoff|share buyback|stock split)\b'),
    ('MATERIAL_CONTRACT', r'\b(?:contract (?:award|win)|awarded? contract|multi.year deal|partnership agreement)\b'),
)


def classify(headline):
    title = str(headline or '')
    return [tag for tag, pattern in PATTERNS if re.search(pattern, title, re.I)]


def valid_utc(value):
    try:
        d = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if not d.tzinfo:
            return None
        return d.astimezone(timezone.utc).isoformat()
    except (ValueError, TypeError):
        return None


def build_catalog(audit):
    if audit.get('mode') != 'NEWS_COVERAGE_AUDIT_READ_ONLY':
        raise ValueError('Expected a news-audit report')
    if audit.get('health') != 'OK_DATA_COVERAGE_DIAGNOSTIC' or not audit.get('all_pages_fetched'):
        raise ValueError('Incomplete coverage: fetch all pages before cataloging')
    if not isinstance(audit.get('articles'), list):
        raise ValueError('Audit report has no article records')
    requested = set(audit.get('requested_symbols') or [])
    seen = set()
    events = []
    counts = Counter()
    excluded = 0
    for a in audit['articles']:
        if not isinstance(a, dict):
            excluded += 1
            continue
        relevant = sorted(requested.intersection(a.get('symbols') or []))
        if not relevant:
            excluded += 1
            continue
        timestamp = valid_utc(a.get('created_at'))
        if not timestamp or not a.get('url'):
            excluded += 1
            continue
        key = str(a.get('id') or (a.get('headline'), timestamp))
        if key in seen:
            excluded += 1
            continue
        seen.add(key)
        tags = classify(a.get('headline'))
        for tag in tags:
            counts[tag] += 1
        events.append({
            'article_id': a.get('id'), 'provider_created_at_utc': timestamp,
            'headline': a.get('headline'), 'source': a.get('source'),
            'source_url': a.get('url'), 'requested_symbols_mentioned': relevant,
            'candidate_types': tags,
            'classification': 'POTENTIAL_CATALYST_UNVERIFIED' if tags else 'GENERAL_NEWS_UNVERIFIED',
            'primary_source_verified': False, 'analyst_consensus_verified': False,
            'surprise_verified': False, 'first_tradable_availability_verified': False,
            'direction': 'UNKNOWN', 'strategy_eligible': False,
        })
    events.sort(key=lambda a: (a['provider_created_at_utc'], str(a['article_id'])))
    potential = sum(bool(x['candidate_types']) for x in events)
    return {
        'mode': 'NEWS_EVENT_CATALOG_READ_ONLY', 'health': 'OK_UNVERIFIED_LEADS',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'audit_interval': {'start': audit.get('start'), 'end': audit.get('end')},
        'requested_symbols': sorted(requested),
        'summary': {'relevant_articles': len(events), 'potential_catalyst_headlines': potential,
                    'general_news_headlines': len(events)-potential,
                    'excluded_records': excluded, 'type_mentions': dict(counts),
                    'verified_events': 0},
        'events': events,
        'strategy_eligible': False, 'orders_sent': 0, 'authorized_to_trade': False,
        'limitations': [
            'Headline tags are keyword leads, not a verified or exhaustive classification.',
            'Published timestamps do not prove first tradable availability.',
            'Neither actual earnings nor contemporaneous consensus are independently verified.',
            'Direction, surprise magnitude, and materiality are UNKNOWN; no market reaction is analyzed.',
            'Only explicitly requested symbols are counted as relevant; unrelated symbol mentions are excluded.',
            'Zero potential headlines is not evidence that there were no material catalysts.',
        ],
    }


def main():
    p = argparse.ArgumentParser(description='Build conservative catalyst leads from a complete news-audit JSON')
    p.add_argument('--input', default='/app/reports/news/coverage.json')
    p.add_argument('--output', default='/app/reports/news/catalog.json')
    args = p.parse_args()
    try:
        if Path(args.input).resolve() == Path(args.output).resolve():
            raise ValueError('Input and output must differ')
        report = build_catalog(json.loads(Path(args.input).read_text(encoding='utf-8')))
        code = 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        report = {'mode': 'NEWS_EVENT_CATALOG_READ_ONLY', 'health': 'BLOCKED_INPUT',
                  'error_type': type(exc).__name__, 'message': str(exc),
                  'strategy_eligible': False, 'orders_sent': 0, 'authorized_to_trade': False}
        code = 2
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ('events', 'limitations')}, ensure_ascii=False))
    return code

if __name__ == '__main__':
    raise SystemExit(main())
