"""Prospective decision journal: append-only DAILY observations, no broker writes.

This module never sends orders or attributes paper P&L to NO_TRADE ideas.
Returns are observational close-to-close from future distinct daily snapshots only.
"""
import argparse
import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

DEFAULT_REPORT = '/app/reports/swing/latest.json'
DEFAULT_JOURNAL = '/app/reports/shadow/observations.jsonl'
DEFAULT_SUMMARY = '/app/reports/shadow/summary.json'


def summarize(records):
    # Only observation dates strictly newer than the entry close. Intra-day
    # repeat snapshots of same session do not count as distinct observations.
    days = sorted({r['market_day'] for r in records})
    by_day = {day: {} for day in days}
    for record in records:
        by_day[record['market_day']] = record['assets']
    horizons = (5, 10, 20)
    outcomes = []
    for index, day in enumerate(days):
        for symbol, entry in by_day[day].items():
            for horizon in horizons:
                if index + horizon >= len(days):
                    continue
                exit_day = days[index + horizon]
                exit_item = by_day[exit_day].get(symbol)
                if not exit_item or entry['close'] <= 0 or exit_item['close'] <= 0:
                    continue
                # Observational opportunity cost, NOT executed order P&L.
                change = round((exit_item['close'] / entry['close'] - 1) * 100, 4)
                spy_entry = by_day[day].get('SPY')
                spy_exit = by_day[exit_day].get('SPY')
                spy_change = (round((spy_exit['close'] / spy_entry['close'] - 1) * 100, 4)
                              if spy_entry and spy_exit and spy_entry['close'] > 0 else None)
                outcomes.append({'entry_date': day, 'observation_date': exit_day,
                                 'symbol': symbol, 'horizon_observed_sessions': horizon,
                                 'decision': entry['decision'], 'blockers': entry['blockers'],
                                 'close_to_close_pct': change,
                                 'spy_same_period_pct': spy_change,
                                 'excess_vs_spy_pct': round(change - spy_change, 4) if spy_change is not None else None})
    return {'mode': 'SHADOW_OBSERVATION_ONLY', 'orders_sent': 0,
            'unique_observation_days': len(days), 'first_day': days[0] if days else None,
            'last_day': days[-1] if days else None, 'recorded_decisions': sum(len(x) for x in by_day.values()),
            'matured_outcomes': len(outcomes), 'outcomes': outcomes,
            'limitations': ['No orders or hypothetical fills; observational returns are not strategy P&L.',
                            'Horizon uses observed days, not guaranteed consecutive trading sessions.',
                            'A missing market date delays maturity; survivorship and selection effects remain.',
                            'Daily close cannot determine intraday stop or fill; gaps, costs and FX omitted.']}


def capture(report, journal=DEFAULT_JOURNAL, summary=DEFAULT_SUMMARY, now_ny=None):
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        raise ValueError('LIVE trading must remain disabled')
    if report.get('mode') != 'READ_ONLY_RESEARCH_NO_ORDERS' or report.get('health') != 'OK_RESEARCH_ONLY':
        raise ValueError('Only healthy read-only radar reports may be journaled')
    if report.get('paper_execution_authorized') is not False or report.get('live_execution_authorized') is not False:
        raise ValueError('Order authorization must be false')
    paper = report.get('paper_account', {})
    if paper.get('status') != 'READ_ONLY_DIAGNOSTIC_NO_ORDERS' or paper.get('paper_execution_authorized') is not False:
        raise ValueError('Paper audit unavailable; fail closed')
    if paper.get('open_orders') != 0 or paper.get('open_positions') != 0:
        raise ValueError('Existing account orders or positions require manual review')
    candidates = report.get('candidates', [])
    if not candidates or report.get('errors'):
        raise ValueError('No candidates or degraded market feed')
    asset_days = {c['technical']['as_of'] for c in candidates}
    if len(asset_days) != 1:
        raise ValueError('Different candle dates; no snapshot')
    day = next(iter(asset_days))
    clock = now_ny or datetime.now(ZoneInfo('America/New_York'))
    if clock.date().isoformat() == day and (clock.hour, clock.minute) < (16, 15):
        raise ValueError('Do not journal incomplete current-session daily bars before 16:15 New York time')
    if clock.date().isoformat() < day:
        raise ValueError('Future-dated market candle')
    if (datetime.now(timezone.utc).date() - datetime.fromisoformat(day).date()).days > 5:
        raise ValueError('Stale market day')
    assets = {}
    for c in candidates:
        tech, ranking = c['technical'], c['ranking']
        symbol = c['symbol']
        if symbol in assets or ranking.get('signal') != 'NO_TRADE' or ranking.get('order_eligible') is not False:
            raise ValueError('Duplicate symbol or unapproved trading signal')
        close = float(tech['last_close'])
        if not 0 < close < 1_000_000:
            raise ValueError('Invalid close price')
        assets[symbol] = {'close': close, 'decision': 'NO_TRADE',
                          'attention_score': ranking['attention_score'],
                          'blockers': ranking.get('blockers', []),
                          'fundamental_status': c.get('fundamental', {}).get('status')}
    p = Path(journal)
    p.parent.mkdir(parents=True, exist_ok=True)
    records = []
    if p.exists():
        with p.open() as stream:
            for line in stream:
                if line.strip():
                    records.append(json.loads(line))
    if any(rec['market_day'] == day for rec in records):
        # Do not rewrite the original decision with later-in-day information.
        duplicate = True
    else:
        entry = {'market_day': day, 'captured_at_utc': datetime.now(timezone.utc).isoformat(),
                 'source_report_created_at_utc': report.get('created_at_utc'),
                 'assets': assets, 'paper_account_status': paper['status']}
        with p.open('a') as stream:
            stream.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + '\n')
        records.append(entry)
        duplicate = False
    result = summarize(records)
    result['duplicate_market_day_skipped'] = duplicate
    result['journal_path'] = str(p)
    target = Path(summary)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(target)
    print(json.dumps({'mode': result['mode'], 'observation_days': result['unique_observation_days'],
                      'matured_outcomes': result['matured_outcomes'],
                      'duplicate_skipped': duplicate, 'orders_sent': 0}))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', default=DEFAULT_REPORT)
    parser.add_argument('--journal', default=DEFAULT_JOURNAL)
    parser.add_argument('--summary', default=DEFAULT_SUMMARY)
    args = parser.parse_args()
    capture(json.loads(Path(args.report).read_text()), args.journal, args.summary)


if __name__ == '__main__':
    main()
