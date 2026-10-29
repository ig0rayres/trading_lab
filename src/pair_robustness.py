#!/usr/bin/env python3
"""Read-only pair result robustness audit. No market access or orders.

Stress adds incremental execution costs ON TOP of baseline model's costs.
The percentage impact is not a quote for actual borrow availability/cost.
"""
import argparse
import csv
import json
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path


def stat(rows):
    if not rows:
        return {'n': 0, 'mean_net_pct': None, 'profit_factor': None, 'win_rate_pct': None}
    p = [r['net_pct'] for r in rows]
    pos = sum(v for v in p if v > 0)
    neg = -sum(v for v in p if v < 0)
    return {'n':len(p), 'mean_net_pct':round(statistics.mean(p),6),
            'profit_factor':round(pos/neg,4) if neg else None,
            'win_rate_pct':round(100*sum(v>0 for v in p)/len(p),2)}


def analyze(records):
    rows = []
    for rec in records:
        pair = rec.get('symbol','')
        if ':' not in pair or len(pair.split(':')) != 2:
            raise ValueError('Invalid pair symbol')
        try:
            d = date.fromisoformat(rec['date'])
            p = float(rec['net_pct'])
        except (ValueError,KeyError) as exc:
            raise ValueError('Invalid date/net_pct') from exc
        if not -200 < p < 200:
            raise ValueError('Impossible net_pct')
        rows.append({'date':str(d),'symbol':pair,'net_pct':p})
    rows.sort(key=lambda r:(r['date'],r['symbol']))
    bypair=defaultdict(list)
    byday=defaultdict(list)
    for row in rows:
        bypair[row['symbol']].append(row)
        byday[row['date']].append(row)
    dates=sorted(byday)
    split=len(dates)//2
    earlier=set(dates[:split]); later=set(dates[split:])
    # A 1bp additional one-way charge on each of both equal-notional legs
    # corresponds to 2bp of combined pair capital on a round trip = 0.02%.
    # This is additive; costs already modeled in v1.0 are NOT replaced.
    stresses={str(bps):stat([{'net_pct':r['net_pct']-2*bps/100} for r in rows])
              for bps in (0,2.5,5,10,20)}
    leave_one_pair_out={pair:stat([r for r in rows if r['symbol'] != pair]) for pair in sorted(bypair)}
    result={'status':'ROBUSTNESS_SCREEN_NOT_PROFITABILITY_PROOF',
            'baseline':stat(rows), 'distinct_days':len(dates),
            'by_pair':{p:stat(v) for p,v in sorted(bypair.items())},
            'earlier':stat([r for r in rows if r['date'] in earlier]),
            'later':stat([r for r in rows if r['date'] in later]),
            'additional_one_way_bps_per_leg':stresses,
            'leave_one_pair_out':leave_one_pair_out,
            'breakeven_additional_bps_per_leg':round(statistics.mean([r['net_pct'] for r in rows])*50,4) if rows else None,
            'is_robust':False,
            'warnings':['No independent holdout: chronological split descriptive only.',
                        'Stress bps are incremental on each leg over modeled baseline; borrow fees, short availability, margin, halts and impact remain unmodeled.',
                        'A pooled trade mean is not portfolio PnL; same-day pair trades correlated.',
                        'Ten trades cannot establish robust statistical profitability.',
                        'No real orders permitted.']}
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--report',required=True,help='v1.0 external-research output directory')
    p.add_argument('--output',required=True,help='JSON output file')
    a=p.parse_args()
    report=Path(a.report)
    source=report/'pair_trades.csv'
    summary=report/'summary.json'
    if not source.is_file() or not summary.is_file():
        p.error('Require pair_trades.csv and summary.json in report directory')
    meta=json.loads(summary.read_text())
    if meta.get('status')!='EXPLORATORY_HYPOTHESES_NOT_REPRODUCED_PUBLICATION_OR_LIVE_APPROVED':
        p.error('Unexpected report type')
    with source.open(newline='') as f:
        result=analyze(list(csv.DictReader(f)))
    expected=meta.get('pair_ratio_z',{}).get('n')
    if expected != result['baseline']['n']:
        p.error('CSV count does not match summary')
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
