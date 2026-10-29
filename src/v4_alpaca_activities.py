"""Read-only Alpaca Paper FILL activity intake; never claims complete history or verified fees.

Fetches bounded pages via allowlisted GET endpoint. Output is an evidence report,
not directly eligible for FIFO profit computation until completeness and fees
have been independently established.
"""
import argparse
import json
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from .paper_audit import PAPER_URL, validate_env
except ImportError:
    from paper_audit import PAPER_URL, validate_env


def positive(value, label):
    try:
        v = Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        raise ValueError('INVALID_' + label)
    if not v.is_finite() or v <= 0:
        raise ValueError('INVALID_' + label)
    return v


def parse_activity(item):
    if not isinstance(item, dict) or item.get('activity_type') != 'FILL':
        raise ValueError('NOT_FILL_ACTIVITY')
    ident = item.get('id')
    symbol = item.get('symbol')
    side = item.get('side')
    when = item.get('transaction_time')
    if not isinstance(ident, str) or not ident.strip():
        raise ValueError('INVALID_ACTIVITY_ID')
    if not isinstance(symbol, str) or not symbol.strip() or symbol.upper() != symbol:
        raise ValueError('INVALID_SYMBOL')
    if side not in ('buy', 'sell'):
        raise ValueError('INVALID_SIDE')
    if not isinstance(when, str) or not when:
        raise ValueError('INVALID_TIMESTAMP')
    try:
        dt = datetime.fromisoformat(when.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('INVALID_TIMESTAMP')
    if dt.tzinfo is None:
        raise ValueError('NAIVE_TIMESTAMP')
    qty = positive(item.get('qty'), 'QTY')
    price = positive(item.get('price'), 'PRICE')
    return {'id': ident, 'symbol': symbol, 'side': side, 'qty': str(qty),
            'price': str(price), 'timestamp': dt.astimezone(timezone.utc).isoformat(),
            'order_id': item.get('order_id') if isinstance(item.get('order_id'), str) else None,
            'fee': None, 'fee_verified': False}


def normalize_pages(pages, *, hit_page_limit=False):
    if not isinstance(pages, list) or not pages:
        raise ValueError('NO_PAGES')
    found = {}
    newest_to_oldest = []
    for page in pages:
        if not isinstance(page, list):
            raise ValueError('INVALID_PAGE')
        for raw in page:
            event = parse_activity(raw)
            ident = event['id']
            if ident in found:
                if found[ident] != event:
                    raise ValueError('CONFLICTING_DUPLICATE_ACTIVITY')
                raise ValueError('DUPLICATE_ACTIVITY')
            found[ident] = event
            newest_to_oldest.append(event)
    chronological = sorted(newest_to_oldest, key=lambda e: (e['timestamp'], e['id']))
    return {'schema_version': 'v4-alpaca-fills-1', 'source': 'ALPACA_PAPER_ACTIVITIES_GET',
            'mode': 'READ_ONLY', 'currency': 'USD', 'activities': chronological,
            'activity_count': len(chronological), 'pages_received': len(pages),
            'complete': False, 'broker_reconciled': False, 'fees_verified': False,
            'history_boundary_verified': False, 'pagination_limit_hit': bool(hit_page_limit),
            'blocking_reasons': ['ACTIVITY_HISTORY_BOUNDARY_UNVERIFIED', 'FEES_UNVERIFIED',
                                 'POSITION_RECONCILIATION_REQUIRED'],
            'execution_authorized': False, 'orders_sent': 0}


def fetch_pages(env, *, opener=urlopen, max_pages=5, page_size=100):
    validate_env(env)
    if not isinstance(max_pages, int) or not 1 <= max_pages <= 100:
        raise ValueError('INVALID_MAX_PAGES')
    if not isinstance(page_size, int) or not 1 <= page_size <= 100:
        raise ValueError('INVALID_PAGE_SIZE')
    pages = []
    cursor = None
    for _ in range(max_pages):
        args = {'activity_types': 'FILL', 'direction': 'desc', 'page_size': str(page_size)}
        if cursor:
            args['page_token'] = cursor
        url = PAPER_URL + '/v2/account/activities?' + urlencode(args)
        req = Request(url, headers={
            'APCA-API-KEY-ID': env['ALPACA_API_KEY'],
            'APCA-API-SECRET-KEY': env['ALPACA_SECRET_KEY']}, method='GET')
        with opener(req, timeout=15) as response:
            page = json.load(response)
        if not isinstance(page, list):
            raise ValueError('INVALID_API_PAGE')
        pages.append(page)
        if len(page) < page_size:
            return normalize_pages(pages, hit_page_limit=False)
        token = page[-1].get('id') if isinstance(page[-1], dict) else None
        if not isinstance(token, str) or not token or token == cursor:
            raise ValueError('INVALID_PAGE_CURSOR')
        cursor = token
    return normalize_pages(pages, hit_page_limit=True)


def main(argv=None):
    p = argparse.ArgumentParser(description='Read-only Alpaca Paper fill activities')
    p.add_argument('--output', required=True)
    p.add_argument('--max-pages', type=int, default=5)
    args = p.parse_args(argv)
    try:
        path = Path(args.output)
        if path.suffix != '.json' or path.is_symlink():
            raise ValueError('UNSAFE_OUTPUT_PATH')
        report = fetch_pages(os.environ, max_pages=args.max_pages)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix('.json.tmp')
        if tmp.is_symlink():
            raise ValueError('UNSAFE_TEMP_PATH')
        with tmp.open('w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        print(json.dumps({'status': 'PARTIAL_READ_ONLY', 'activities': report['activity_count'],
                          'orders_sent': 0}))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
