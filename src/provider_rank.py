"""Historical signal-provider ranking. Offline only; no brokerage calls.

Input JSON: {"providers": [{"id": "...", "asset_classes": ["us_equity"],
 "verified": true, "track_record_start": ISO8601, "trades": [
 {"closed_at": ISO8601, "net_pnl_pct": number, "risk_pct": number}]}]}
net_pnl_pct is return on the provider's allocated capital after all costs.
Returns MUST be from actual chronological closed trades, not marketing summaries.
"""
import argparse
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path


def dt(value):
    out = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if out.tzinfo is None:
        raise ValueError('timezone required')
    return out.astimezone(timezone.utc)


def analyze(data, now=None, window_days=180, min_trades=30):
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(days=window_days)
    result = []
    ids = set()
    for p in data.get('providers', []):
        pid = p['id']
        if pid in ids: raise ValueError('duplicate provider ID')
        ids.add(pid)
        reasons = []
        if p.get('verified') is not True: reasons.append('UNVERIFIED_HISTORY')
        try:
            inception = dt(p['track_record_start'])
            if inception > start: reasons.append('INSUFFICIENT_HISTORY')
            if inception > now: reasons.append('FUTURE_INCEPTION')
        except (KeyError, ValueError, TypeError):
            reasons.append('INVALID_INCEPTION')
        if p.get('asset_classes') != ['us_equity']:
            reasons.append('UNSUPPORTED_ASSET_CLASS')
        trades = []
        try:
            for t in p['trades']:
                closed = dt(t['closed_at'])
                pnl = float(t['net_pnl_pct'])
                risk = float(t['risk_pct'])
                if not all(map(math.isfinite, (pnl, risk))) or risk <= 0 or risk > 100:
                    raise ValueError('non-finite or invalid risk')
                if closed > now: raise ValueError('future trade')
                if start <= closed <= now:
                    trades.append((closed, pnl, risk))
        except (KeyError, ValueError, TypeError, OverflowError):
            reasons.append('INVALID_TRADE_DATA')
            trades = []
        trades.sort(key=lambda x: x[0])
        if len(trades) < min_trades: reasons.append('LOW_SAMPLE')
        equity, high, dd = 1.0, 1.0, 0.0
        wins = 0
        for _, pnl, _ in trades:
            # Cannot interpret a loss worse than -100% as a capital return.
            if pnl < -100: reasons.append('INVALID_RETURN');break
            equity *= max(0, 1 + pnl/100)
            high = max(high, equity)
            dd = max(dd, (high - equity)/high*100)
            wins += pnl > 0
        net = (equity-1)*100
        if net <= 0: reasons.append('NONPOSITIVE_NET_RETURN')
        if dd > 20: reasons.append('EXCESSIVE_DRAWDOWN')
        # Conservative score; penalizes drawdown and weak history.
        score = net / (1+dd) * min(1, len(trades)/60)
        result.append({'provider_id': pid,'eligible': not reasons,'reasons': sorted(set(reasons)),
                       'trades':len(trades),'net_return_pct':round(net,3),
                       'max_drawdown_pct':round(dd,3),'win_rate_pct':round(wins/len(trades)*100,2) if trades else 0,
                       'score':round(score,5)})
    result.sort(key=lambda x:(not x['eligible'], -x['score'], x['provider_id']))
    eligible = [x for x in result if x['eligible']]
    return {'mode':'PROVIDER_RANKING_RESEARCH_ONLY','window_days':window_days,
            'period_start':start.isoformat(),'period_end':now.isoformat(),
            'top_10':result[:10], 'paper_priority_top_3':[x['provider_id'] for x in eligible[:3]],
            'orders_sent':0, 'execution_authorized':False,
            'warning':'Ranking is retrospective and may overfit. Provider approvals and broker execution require separate controls.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True)
    ap.add_argument('--output',default='/app/reports/providers/latest.json')
    args=ap.parse_args()
    report=analyze(json.loads(Path(args.input).read_text()))
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
