"""Automated read-only swing watchlist. Research, not orders or investment advice."""
import argparse
import json
import math
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from zoneinfo import ZoneInfo

DEFAULT_SYMBOLS = 'AAPL,MSFT,NVDA,AMD,GOOGL,AMZN,META,TSLA,AVGO,PLTR,SPY,QQQ'
DEFAULT_OUTPUT = '/app/reports/swing/latest.json'
ETF_SYMBOLS = frozenset({'SPY', 'QQQ'})
UA = os.getenv('MARKET_USER_AGENT', 'TradingLabResearch/1.5 (read-only market research)')
BAD_HEADLINE = ('lawsuit', 'investigation', 'probe', 'recall', 'downgrade', 'fraud', 'misses', 'warning', 'bankruptcy')
GOOD_HEADLINE = ('beats estimates', 'raises guidance', 'upgrades', 'record revenue', 'wins contract')


def http_json(url, timeout=12):
    request = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(request, timeout=timeout) as res:
        return json.load(res)


def http_text(url, timeout=12):
    request = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/rss+xml, application/xml, text/xml'})
    with urllib.request.urlopen(request, timeout=timeout) as res:
        return res.read(500000)


def yahoo_daily(symbol, fetch=http_json):
    symbol_q = urllib.parse.quote(symbol, safe='')
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + symbol_q + '?range=9mo&interval=1d'
    data = fetch(url)
    result = (data.get('chart', {}).get('result') or [None])[0]
    if not result:
        raise ValueError('No daily candles')
    quote = result['indicators']['quote'][0]
    adjusted = result['indicators'].get('adjclose', [{}])[0].get('adjclose') or []
    dates = result.get('timestamp', [])
    candles = []
    for i, stamp in enumerate(dates):
        try:
            close, high, low, volume = (quote[k][i] for k in ('close', 'high', 'low', 'volume'))
            if None in (close, high, low, volume) or close <= 0 or low <= 0 or high < low:
                continue
            # Use raw coherent OHLC for indicators; adjusted closes would distort relative OHLC.
            candles.append({'day': datetime.fromtimestamp(stamp, timezone.utc).date().isoformat(),
                            'close': float(close), 'high': float(high), 'low': float(low),
                            'volume': int(volume)})
        except (IndexError, TypeError, ValueError, KeyError):
            continue
    if len(candles) < 65:
        raise ValueError('Fewer than 65 valid daily candles')
    return candles


def technical(candles, today=None):
    closes = [x['close'] for x in candles]
    volumes = [x['volume'] for x in candles]
    latest_day = datetime.fromisoformat(candles[-1]['day']).date()
    now = today or datetime.now(timezone.utc).date()
    age = (now - latest_day).days
    # More than 5 calendar days indicates unreliable data, not just a weekend/holiday.
    if age < 0 or age > 5:
        raise ValueError('Daily bars stale or future-dated')
    gains, losses = [], []
    for a, b in zip(closes[-15:-1], closes[-14:]):
        diff = b - a
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    ag, al = mean(gains), mean(losses)
    rsi = 100 if al == 0 and ag > 0 else (50 if al == 0 else 100 - 100 / (1 + ag / al))
    trs = []
    for i in range(len(candles)-14, len(candles)):
        c, prev = candles[i], candles[i-1]['close']
        trs.append(max(c['high'] - c['low'], abs(c['high'] - prev), abs(c['low'] - prev)))
    close, sma20, sma50 = closes[-1], mean(closes[-20:]), mean(closes[-50:])
    change_20 = (close / closes[-21] - 1) * 100
    volume_ratio = volumes[-1] / mean(volumes[-21:-1]) if mean(volumes[-21:-1]) else 0
    atr = mean(trs)
    trend = 'UP' if close > sma20 > sma50 else ('DOWN' if close < sma20 < sma50 else 'MIXED')
    return {'as_of': latest_day.isoformat(), 'last_close': round(close, 3),
            'sma20': round(sma20, 3), 'sma50': round(sma50, 3), 'rsi14': round(rsi, 2),
            'atr14': round(atr, 3), 'change20_pct': round(change_20, 2),
            'volume_ratio20': round(volume_ratio, 2), 'trend': trend,
            'support20': round(min(x['low'] for x in candles[-20:]), 3),
            'resistance20': round(max(x['high'] for x in candles[-20:]), 3),
            'data_age_days': age}


def news(symbol, fetch=http_text):
    # Google News RSS is a headline aggregator, not a verified market-news feed.
    phrase = urllib.parse.quote('"' + symbol + '" stock earnings market', safe='')
    url = f'https://news.google.com/rss/search?q={phrase}&hl=en-US&gl=US&ceid=US:en'
    root = ET.fromstring(fetch(url))
    items = []
    for item in root.findall('./channel/item')[:8]:
        title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        pub = (item.findtext('pubDate') or '').strip()
        if not title or not link.startswith('https://'):
            continue
        lower = title.lower()
        tone = 'CAUTION' if any(t in lower for t in BAD_HEADLINE) else ('POSITIVE_CLAIM' if any(t in lower for t in GOOD_HEADLINE) else 'UNVERIFIED')
        items.append({'title': title[:250], 'url': link, 'published': pub, 'headline_tag': tone})
    return items


def sec_fundamentals(symbol, ticker_map, fetch=http_json):
    """Conservative SEC extraction: comparable annual facts only, or explicitly unavailable.

    No financial score is emitted when the data cannot be matched by reporting
    period. Select annual 10-K duration records, NOT the newest filed value from
    potentially old periods or a YTD 10-Q.
    """
    if symbol in ETF_SYMBOLS:
        return {'status': 'NOT_APPLICABLE', 'reason': 'ETF: issuer earnings do not apply; assess exposure separately'}
    record = ticker_map.get(symbol)
    if not record:
        return {'status': 'UNAVAILABLE', 'reason': 'No verified SEC issuer mapping'}
    cik = str(record).zfill(10)
    data = fetch(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json')
    facts = data.get('facts', {}).get('us-gaap', {})
    def annual(tag_list):
        found = []
        for tag in tag_list:
            for v in facts.get(tag, {}).get('units', {}).get('USD', []):
                if v.get('form') != '10-K' or not all(k in v for k in ('start', 'end', 'filed', 'val')):
                    continue
                try:
                    duration = (datetime.fromisoformat(v['end']) - datetime.fromisoformat(v['start'])).days
                    if not 330 <= duration <= 380 or not math.isfinite(float(v['val'])):
                        continue
                    # Ignore records which were filed before the period ended.
                    if v['filed'] < v['end']:
                        continue
                except (ValueError, TypeError, OverflowError):
                    continue
                found.append(v)
        # Prefer latest period, then the most recent filing / amendment.
        return max(found, key=lambda v: (v['end'], v['filed']), default=None)
    revenue = annual(('RevenueFromContractWithCustomerExcludingAssessedTax', 'Revenues', 'SalesRevenueNet'))
    income = annual(('NetIncomeLoss',))
    out = {'status': 'UNAVAILABLE_UNVERIFIED', 'source': 'SEC Company Facts', 'cik': cik,
           'metrics': {}, 'quality_flags': []}
    if not revenue or not income:
        out['quality_flags'].append('MISSING_ANNUAL_REVENUE_OR_NET_INCOME')
        return out
    # Must refer to the exact same 12-month annual window.
    if (revenue['start'], revenue['end']) != (income['start'], income['end']):
        out['quality_flags'].append('MISMATCHED_PERIODS')
        return out
    period_end = datetime.fromisoformat(revenue['end']).date()
    age = (datetime.now(timezone.utc).date() - period_end).days
    if age < 0 or age > 500:
        out['quality_flags'].append('STALE_OR_FUTURE_ANNUAL_FACTS')
        return out
    for name, v in (('revenue', revenue), ('net_income', income)):
        out['metrics'][name] = {'usd': v['val'], 'period_start': v['start'],
                                'period_end': v['end'], 'filed': v['filed'], 'form': v['form']}
    out['status'] = 'ANNUAL_COMPARABLE'
    out['period_end'] = revenue['end']
    out['financial_data_age_days'] = age
    out['quality_flags'].append('ANNUAL_ONLY_NO_GROWTH_OR_VALUATION')
    return out


def sec_tickers(fetch=http_json):
    raw = fetch('https://www.sec.gov/files/company_tickers.json')
    return {str(v.get('ticker','')).upper(): v['cik_str'] for v in raw.values() if 'cik_str' in v}


def rank(tech, headlines, fund, symbol='', paper=None):
    """Quality-first attention score: never calls attention a buy recommendation."""
    problems = []
    if tech['trend'] != 'UP':
        problems.append('NO_CONFIRMED_UPTREND')
    if tech['data_age_days'] > 3:
        problems.append('STALE_DAILY_PRICES')
    if tech['volume_ratio20'] < 0.8:
        problems.append('WEAK_VOLUME_CONFIRMATION')
    if not 40 <= tech['rsi14'] <= 70:
        problems.append('MOMENTUM_OUTSIDE_CONSERVATIVE_RANGE')
    if fund.get('status') not in ('ANNUAL_COMPARABLE', 'NOT_APPLICABLE'):
        problems.append('FUNDAMENTALS_NOT_COMPARABLE')
    # Google News RSS headlines are UNVERIFIED even if keyword-tagged.
    problems.append('CATALYST_NOT_PRIMARY_SOURCE_VERIFIED')
    if not headlines:
        problems.append('NO_NEWS_CONTEXT')
    if any(n.get('headline_tag') == 'CAUTION' for n in headlines):
        problems.append('POTENTIAL_NEGATIVE_CATALYST')
    atr = float(tech.get('atr14') or 0)
    price = float(tech.get('last_close') or 0)
    stop_distance = 2 * atr
    if not 0 < stop_distance < price:
        problems.append('STOP_DISTANCE_INVALID')
    # This is a hypothetical position-sizing ceiling, not a protective stop guarantee.
    capital_usd = 0.0
    risk_usd = 0.0
    if isinstance(paper, dict) and paper.get('status') == 'READ_ONLY_DIAGNOSTIC_NO_ORDERS':
        try:
            capital_usd = float(paper['capital_ceiling_usd'])
            risk_usd = float(paper['planned_risk_per_trade_usd'])
        except (ValueError, TypeError, KeyError):
            pass
    if capital_usd <= 0 or risk_usd <= 0:
        problems.append('RISK_BUDGET_NOT_VERIFIED')
    # At most one third of portfolio per idea, AND 1% at 2-ATR stop.
    shares_risk = (risk_usd / stop_distance) if stop_distance > 0 else 0
    shares_budget = (capital_usd / 3 / price) if price > 0 else 0
    shares = round(max(0, min(shares_risk, shares_budget)), 6)
    score = (3 if tech['trend'] == 'UP' else 0) + (2 if 45 <= tech['rsi14'] <= 65 else 0) + (2 if tech['volume_ratio20'] >= 1 else 0)
    score += (2 if fund.get('status') == 'ANNUAL_COMPARABLE' else 0)
    score -= 2 * int(any(n.get('headline_tag') == 'CAUTION' for n in headlines))
    return {'attention_score': score, 'classification': 'REVIEW' if len(problems) <= 2 else 'WATCH',
            'evidence_quality': fund.get('status'), 'quality_gate': 'REJECT_NO_TRADE',
            'blockers': problems, 'order_eligible': False, 'signal': 'NO_TRADE',
            'hypothetical_risk': {'atr_stop_distance_usd': round(stop_distance, 3),
                                  'shares_cap_fractional_theoretical': shares,
                                  'position_notional_usd': round(shares * price, 2),
                                  'planned_loss_usd_if_stop_fills': round(shares * stop_distance, 2),
                                  'gap_risk_unbounded_by_stop': True},
            'reason': 'Preserve capital: no verified catalyst, no proven positive edge, no orders.'}


def run(symbols, output, use_paper=True):
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        raise ValueError('Live trading must remain disabled')
    symbols = list(dict.fromkeys(x.strip().upper() for x in symbols.split(',') if x.strip()))
    if not symbols or len(symbols) > 30 or any(not re.fullmatch(r'[A-Z.\-]{1,8}', s) for s in symbols):
        raise ValueError('Invalid watchlist')
    result = {'version': '1.7', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
              'mode': 'READ_ONLY_RESEARCH_NO_ORDERS', 'method': 'technical + headline screening + SEC company facts',
              'reference_modules': ['trader-scanner', 'trader-news', 'trader-analyst', 'trader-risk', 'trader-budget'],
              'paper_execution_authorized': False, 'live_execution_authorized': False,
              'universe': symbols, 'candidates': [], 'errors': [],
              'limitations': ['Headline labels are keyword-based; news not independently verified.',
                              'SEC comparable annual revenue/income only; not a valuation signal.',
                              'No causal/prospective performance validation; no buy/sell signals.',
                              'Yahoo finance endpoint is unofficial and may throttle or change.']}
    if use_paper:
        try:
            from paper_audit import audit, get_json, validate_env
            fx = validate_env(os.environ)
            result['paper_account'] = audit(get_json('/v2/account', os.environ),
                                            get_json('/v2/positions', os.environ),
                                            get_json('/v2/orders?status=open&limit=500', os.environ), fx)
        except Exception:
            # Fail closed: do not claim the account is healthy and avoid printing credentials.
            result['paper_account'] = {'status': 'UNAVAILABLE_OR_CONFIGURATION_ERROR', 'flags': ['PAPER_AUDIT_FAILED']}
    try:
        tickers = sec_tickers()
    except Exception:
        tickers = {}
        result['errors'].append({'source': 'SEC_TICKER_MAP', 'error': 'Unavailable'})
    for symbol in symbols:
        try:
            tech = technical(yahoo_daily(symbol))
        except Exception:
            result['errors'].append({'symbol': symbol, 'source': 'DAILY_PRICE', 'error': 'Data unavailable or stale'})
            continue
        try:
            headlines = news(symbol)
        except Exception:
            headlines = []
            result['errors'].append({'symbol': symbol, 'source': 'NEWS', 'error': 'Feed unavailable'})
        try:
            fundamental = sec_fundamentals(symbol, tickers)
        except Exception:
            fundamental = {'status': 'UNAVAILABLE', 'reason': 'SEC request failed'}
            result['errors'].append({'symbol': symbol, 'source': 'SEC_FACTS', 'error': 'Data unavailable'})
        result['candidates'].append({'symbol': symbol, 'technical': tech, 'headlines': headlines,
                                     'fundamental': fundamental, 'ranking': rank(tech, headlines, fundamental, symbol, result.get('paper_account'))})
    result['candidates'].sort(key=lambda x: (len(x['ranking']['blockers']), -x['ranking']['attention_score'], x['symbol']))
    if not result['candidates']:
        result['health'] = 'NO_MARKET_DATA'
    elif result['errors']:
        result['health'] = 'PARTIAL_DATA'
    else:
        result['health'] = 'OK_RESEARCH_ONLY'
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)
    print(json.dumps({'health': result['health'], 'candidates': len(result['candidates']),
                      'errors': len(result['errors']), 'output': str(path), 'orders_sent': 0}))
    return result


def schedule(symbols, output, interval):
    if interval < 15 or interval > 1440:
        raise ValueError('Minimum scan interval is 15 minutes')
    print('Swing radar scheduler started; NY weekdays 09:30-16:00 + 16:15 ET; READ ONLY; no orders. Market holidays are NOT filtered.', flush=True)
    last_regular = None
    last_eod = None
    while True:
        ny = datetime.now(ZoneInfo('America/New_York'))
        today = ny.date().isoformat()
        minute = ny.hour * 60 + ny.minute
        if ny.weekday() < 5:
            if 570 <= minute < 960 and (last_regular is None or time.monotonic() - last_regular >= interval * 60):
                snapshot = run(symbols, output)
                from shadow_journal import capture
                if snapshot.get('health') == 'OK_RESEARCH_ONLY' and snapshot.get('paper_account', {}).get('status') == 'READ_ONLY_DIAGNOSTIC_NO_ORDERS':
                    try:
                        capture(snapshot)
                    except ValueError as error:
                        print('Shadow journal skipped:', type(error).__name__, flush=True)
                last_regular = time.monotonic()
            if minute >= 975 and last_eod != today:
                snapshot = run(symbols, output)
                from shadow_journal import capture
                if snapshot.get('health') == 'OK_RESEARCH_ONLY' and snapshot.get('paper_account', {}).get('status') == 'READ_ONLY_DIAGNOSTIC_NO_ORDERS':
                    try:
                        capture(snapshot)
                    except ValueError as error:
                        print('Shadow journal skipped:', type(error).__name__, flush=True)
                last_eod = today
        time.sleep(60)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--symbols', default=os.getenv('SWING_SYMBOLS', DEFAULT_SYMBOLS))
    p.add_argument('--output', default=DEFAULT_OUTPUT)
    p.add_argument('--schedule', action='store_true')
    p.add_argument('--interval-minutes', type=int, default=30)
    p.add_argument('--skip-paper', action='store_true', help='Research standalone without broker snapshot')
    args = p.parse_args()
    if args.schedule:
        if args.skip_paper:
            raise SystemExit('--skip-paper is not supported in scheduled mode')
        schedule(args.symbols, args.output, args.interval_minutes)
    else:
        run(args.symbols, args.output, use_paper=not args.skip_paper)


if __name__ == '__main__':
    main()
