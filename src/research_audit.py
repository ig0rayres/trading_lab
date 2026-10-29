#!/usr/bin/env python3
"""Read-only, conservative research screening. No order execution or strategy optimization."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

MIN_EVALUATIONS = 100
MIN_UNIQUE_DAYS = 30


def inspect_report(path):
    folder = Path(path)
    report = json.loads((folder / 'summary.json').read_text(encoding='utf-8'))
    if report.get('status') != 'MULTISTRATEGY_EXPLORATORY_NOT_VALIDATED':
        raise ValueError('Expected v0.8 multistrategy exploratory report')
    with (folder / 'trades.csv').open(newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    grouped = {}
    for row in rows:
        key = (row.get('strategy', ''), str(row.get('target_r', '')))
        grouped.setdefault(key, []).append(row)
    candidates = []
    for name, targets in report['strategies'].items():
        for target, periods in targets.items():
            stats = periods['all']
            t = target[:-1]
            r = grouped.get((name, t), [])
            days = len({x.get('date') for x in r if x.get('date')})
            reasons = []
            n = stats.get('evaluations') or 0
            if n < MIN_EVALUATIONS:
                reasons.append('INSUFFICIENT_EVALUATIONS')
            if days < MIN_UNIQUE_DAYS:
                reasons.append('INSUFFICIENT_DISTINCT_DAYS')
            if stats.get('mean_net_r') is None or stats['mean_net_r'] <= 0:
                reasons.append('NONPOSITIVE_NET_EXPECTANCY')
            if stats.get('profit_factor') is None or stats['profit_factor'] <= 1:
                reasons.append('PROFIT_FACTOR_NOT_ABOVE_ONE')
            earlier, later = periods.get('earlier_sessions', {}), periods.get('later_sessions', {})
            if min(earlier.get('evaluations') or 0, later.get('evaluations') or 0) < 20:
                reasons.append('INSUFFICIENT_TEMPORAL_COVERAGE')
            if (earlier.get('mean_net_r') or 0) <= 0 or (later.get('mean_net_r') or 0) <= 0:
                reasons.append('NONPOSITIVE_IN_ONE_TEMPORAL_SEGMENT')
            # Even passing these gates is research-only: no untouched holdout, point-in-time universe,
            # portfolio simulation or validated execution model in v0.8.
            candidates.append({'strategy': name, 'target': target, 'evaluations': n,
                               'distinct_days': days, 'mean_net_r': stats.get('mean_net_r'),
                               'profit_factor': stats.get('profit_factor'),
                               'screen': 'REJECT_FOR_NOW' if reasons else 'NEEDS_INDEPENDENT_VALIDATION',
                               'reasons': reasons})
    diag_path = folder / 'errors.json'
    errors = json.loads(diag_path.read_text()) if diag_path.exists() else []
    diagnostics = Counter(x.get('reason', 'UNKNOWN') for x in errors if isinstance(x, dict))
    return {'status': 'RESEARCH_SCREEN_NOT_LIVE_APPROVAL',
            'source': str(folder), 'total_evaluations': report.get('total_evaluations'),
            'unique_trades_warning': 'Overlapping strategy and target evaluations are correlated',
            'diagnostics_by_reason': dict(diagnostics), 'candidates': candidates,
            'promoted_to_live': 0, 'warnings': [
              'Screens are not evidence of an edge. No untouched holdout or portfolio simulation.',
              'A positive small sample is never proof of profitability.',
              'Never use this output to place real orders.']}


def main(argv=None):
    p = argparse.ArgumentParser(description='Conservative read-only candidate audit of v0.8 research')
    p.add_argument('--report', required=True)
    p.add_argument('--output')
    args = p.parse_args(argv)
    result = inspect_report(args.report)
    text = json.dumps(result, indent=2)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + '\n', encoding='utf-8')
    print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
