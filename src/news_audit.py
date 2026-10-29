"""Read-only Alpaca historical news coverage audit; no trade signals or orders."""
import argparse
import json
import os
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

HOST = 'https://data.alpaca.markets'
ENDPOINT = '/v1beta1/news'
DEFAULT_SYMBOLS = ('AAPL', 'MSFT', 'NVDA', 'AMD', 'TSLA', 'PLTR')


def parse_date(value):
    try:
        result = datetime.strptime(value, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise ValueError('Dates must be YYYY-MM-DD') from exc
    return result


def validate(args, env):
    if env.get('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        raise ValueError('LIVE_TRADING_ENABLED must be false')
    if env.get('ALPACA_PAPER_TRADE', '').lower() != 'true':
        raise ValueError('ALPACA_PAPER_TRADE must be true')
    if env.get('ALPACA_BASE_URL', '').rstrip('/') != 'https://paper-api.alpaca.markets':
        raise ValueError('ALPACA_BASE_URL must be Alpaca PAPER endpoint')
    if not env.get('ALPACA_API_KEY') or not env.get('ALPACA_SECRET_KEY'):
        raise ValueError('ALPACA_API_KEY and ALPACA_SECRET_KEY required')
    start = parse_date(args.start)
    end = parse_date(args.end)
    if not start < end <= datetime.now(timezone.utc) + timedelta(days=1):
        raise ValueError('Date interval is invalid or in the future')
    if (end - start).days > 366:
        raise ValueError('Limit audit interval to 366 days')
    symbols = [s.strip().upper() for s in args.symbols.split(',') if s.strip()]
    if not 1 <= len(symbols) <= 20 or any(not x.isascii() or not x.replace('.', '').isalnum() for x in symbols):
        raise ValueError('Invalid symbols (1-20 required)')
    if not 1 <= args.pages <= 20:
        raise ValueError('--pages must be 1..20')
    return symbols


def get_page(params, env, opener=urlopen):
    url = HOST + ENDPOINT + '?' + urlencode(params)
    req = Request(url, headers={
        'APCA-API-KEY-ID': env['ALPACA_API_KEY'],
        'APCA-API-SECRET-KEY': env['ALPACA_SECRET_KEY'],
    }, method='GET')
    with opener(req, timeout=20) as response:
        data = json.load(response)
    if not isinstance(data, dict) or not isinstance(data.get('news'), list):
        raise ValueError('Unexpected Alpaca news response')
    return data


def review_articles(items):
    seen = set()
    deduped = []
    count_missing_time = 0
    count_without_url = 0
    sources = Counter()
    symbols = Counter()
    for item in items:
        key = str(item.get('id') or (item.get('headline'), item.get('created_at')))
        if key in seen:
            continue
        seen.add(key)
        published = item.get('created_at')
        try:
            dt = datetime.fromisoformat(str(published).replace('Z', '+00:00'))
            if dt.tzinfo is None:
                raise ValueError('Missing timezone')
        except (ValueError, TypeError):
            count_missing_time += 1
        if not item.get('url'):
            count_without_url += 1
        sources[str(item.get('source') or 'UNSPECIFIED')] += 1
        for symbol in set(item.get('symbols') or []):
            symbols[str(symbol)] += 1
        deduped.append({
            'id': item.get('id'),
            'created_at': published,
            'updated_at': item.get('updated_at'),
            'source': item.get('source'),
            'symbols': item.get('symbols') or [],
            'headline': str(item.get('headline') or '')[:300],
            'url': item.get('url'),
        })
    return {
        'unique_articles': len(deduped),
        'duplicate_articles_removed': len(items) - len(deduped),
        'missing_or_invalid_created_at': count_missing_time,
        'missing_article_url': count_without_url,
        'source_counts': dict(sources),
        'symbol_counts': dict(symbols),
    }, deduped


def run_audit(args, env, getter=get_page):
    symbols = validate(args, env)
    params = {
        'symbols': ','.join(symbols),
        'start': args.start,
        'end': args.end,
        'limit': 50,
        'sort': 'asc',
        'include_content': 'false',
    }
    raw = []
    page_token = None
    last_token = None
    pages = 0
    exhausted = False
    for _ in range(args.pages):
        if page_token:
            params['page_token'] = page_token
        page = getter(params, env)
        pages += 1
        raw.extend(page['news'])
        last_token = page.get('next_page_token')
        if not last_token:
            exhausted = True
            break
        if last_token == page_token:
            raise ValueError('Pagination did not advance')
        page_token = last_token
    counts, records = review_articles(raw)
    return {
        'mode': 'NEWS_COVERAGE_AUDIT_READ_ONLY',
        'health': 'OK_DATA_COVERAGE_DIAGNOSTIC' if exhausted else 'PARTIAL_PAGINATED_COVERAGE',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'provider': 'alpaca_news',
        'requested_symbols': symbols,
        'start': args.start,
        'end': args.end,
        'pages_fetched': pages,
        'all_pages_fetched': exhausted,
        'coverage': counts,
        'articles': records,
        'earnings_surprise_verified': False,
        'analyst_consensus_verified': False,
        'actual_publication_latency_verified': False,
        'strategy_eligible': False,
        'orders_sent': 0,
        'authorized_to_trade': False,
        'limitations': [
            'News availability may depend on account entitlements and source coverage.',
            'created_at is a provider timestamp; first tradable availability is not established.',
            'News headlines alone do not establish verified earnings surprises or consensus.',
            'A zero article count does not prove that no catalyst existed.',
            'No price, slippage, borrow, or portfolio simulation is performed.',
        ],
    }


def main():
    p = argparse.ArgumentParser(description='Read-only news availability and quality audit')
    p.add_argument('--start', required=True)
    p.add_argument('--end', required=True)
    p.add_argument('--symbols', default=','.join(DEFAULT_SYMBOLS))
    p.add_argument('--pages', type=int, default=3)
    p.add_argument('--output', default='/app/reports/news/coverage.json')
    args = p.parse_args()
    try:
        result = run_audit(args, os.environ)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError) as exc:
        result = {
            'mode': 'NEWS_COVERAGE_AUDIT_READ_ONLY',
            'health': 'BLOCKED_DATA_ACCESS',
            'error_type': type(exc).__name__,
            'http_status': exc.code if isinstance(exc, HTTPError) else None,
            'orders_sent': 0,
            'authorized_to_trade': False,
        }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('articles', 'limitations')}, ensure_ascii=False))
    return 0 if result['health'] != 'BLOCKED_DATA_ACCESS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
