"""Fail-closed risk preview for untrusted research decisions; never submits orders.

Risk approval is *not* execution permission. A decision-cycle observation cannot
be upgraded to verified merely because it has valid prices or a signature.
"""
import argparse
import json
import os
from pathlib import Path

try:
    from .portfolio_risk_v4 import evaluate
except ImportError:
    from portfolio_risk_v4 import evaluate


def assess(report, snapshot=None, tickets=None):
    if not isinstance(report, dict) or report.get('automatic_order_submission') is not False or report.get('paper_approved') is not False or report.get('orders_sent') != 0 or not isinstance(report.get('decisions'), list):
        raise ValueError('UNSAFE_DECISION_REPORT')
    if tickets is not None and not isinstance(tickets, dict):
        raise ValueError('INVALID_TICKETS')
    if snapshot is not None and not isinstance(snapshot, dict):
        raise ValueError('INVALID_SNAPSHOT')
    seen = set()
    results = []
    for item in report['decisions']:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id'] or item['id'] in seen:
            raise ValueError('INVALID_OR_DUPLICATE_DECISION_ID')
        seen.add(item['id'])
        if item.get('decision') != 'RESEARCH_ONLY' or item.get('paper_approved') is not False or item.get('tradable_signal') is not False or item.get('orders_sent') != 0:
            raise ValueError('UNSAFE_DECISION_ITEM')
        reasons = ['RESEARCH_SIGNAL_NOT_EXECUTION_AUTHORIZED']
        # Optional user-supplied tickets are never trusted for verification.
        ticket = (tickets or {}).get(item['id'])
        if ticket is None:
            reasons.append('NO_EXECUTION_TICKET')
        elif not isinstance(ticket, dict):
            reasons.append('INVALID_EXECUTION_TICKET')
        elif ticket.get('market') != item.get('market') or ticket.get('symbol') != item.get('symbol'):
            reasons.append('TICKET_DECISION_MISMATCH')
        else:
            candidate = dict(ticket, verified=False, trading_mode='RESEARCH')
            check = evaluate(candidate, snapshot or {})
            reasons.extend(check['reasons'])
        if snapshot is None:
            reasons.append('NO_RECONCILED_PORTFOLIO_SNAPSHOT')
        results.append({'id': item['id'], 'kind': item.get('kind'), 'market': item.get('market'),
                        'symbol': item.get('symbol'), 'risk_preview': 'BLOCKED',
                        'reasons': sorted(set(reasons)), 'paper_approved': False, 'orders_sent': 0})
    return {'schema_version': 'v4-decision-risk-preview-1', 'status': 'RESEARCH_ONLY',
            'results': results, 'paper_approved': False, 'automatic_order_submission': False,
            'orders_sent': 0, 'note': 'This report does not certify broker reconciliation or permit orders.'}


def main(argv=None):
    p = argparse.ArgumentParser(description='Read-only portfolio-risk preview for decision cycle')
    p.add_argument('--decisions', required=True)
    p.add_argument('--snapshot')
    p.add_argument('--tickets')
    p.add_argument('--output', required=True)
    args = p.parse_args(argv)
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        print(json.dumps({'status': 'BLOCKED_LIVE_FLAG', 'orders_sent': 0})); return 2
    try:
        load = lambda path: json.loads(Path(path).read_text(encoding='utf-8')) if path else None
        report = assess(load(args.decisions), load(args.snapshot), load(args.tickets))
        output = Path(args.output)
        if output.suffix != '.json' or output.is_symlink():
            raise ValueError('UNSAFE_OUTPUT')
        output.parent.mkdir(parents=True, exist_ok=True)
        temp = output.with_suffix('.json.tmp')
        if temp.is_symlink():
            raise ValueError('UNSAFE_TEMP_FILE')
        temp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        temp.replace(output)
        print(json.dumps({'status': report['status'], 'assessments': len(report['results']), 'orders_sent': 0}))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
