"""Read-only rising-star research rankings from Collective2 closed trades.

Never treats a win streak, equity curve, or rank as execution authorization.
"""
import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from strategy_data_adapter import load, num, timestamp

MIN_TRADES = 5
WINDOW_DAYS = 15
PEARL_TOP_N = 10


def pearl_sort_key(row: dict) -> tuple[float, float, float, float]:
  """Inbox pearl ordering: return, PF, shrunk win rate, prodigy score (all descending)."""
  def _num(value: object, default: float = float('-inf')) -> float:
    if value is None:
      return default
    try:
      return float(value)
    except (TypeError, ValueError):
      return default

  return (
    -_num(row.get('reported_pnl_sum')),
    -_num(row.get('profit_factor_reported'), 0.0),
    -_num(row.get('shrunk_win_rate_pct')),
    -_num(row.get('prodigy_score')),
  )


def is_pearl_candidate(item: dict) -> bool:
  if item.get('status') != 'PRODIGY_CANDIDATE_RESEARCH':
    return False
  pnl = item.get('reported_pnl_sum')
  if pnl is None or float(pnl) <= 0:
    return False
  losses = item.get('losses') or 0
  if losses > 0:
    pf = item.get('profit_factor_reported')
    if pf is None or float(pf) < 1:
      return False
  return True


def calculate(base, now=None):
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(days=WINDOW_DAYS)
    ids = sorted({p.name.split('_')[0] for p in base.glob('*_closed_trades.json') if p.name.split('_')[0].isdigit()})
    entries = []
    for sid in ids:
        item = {'provider_id':sid, 'status':'UNSCORABLE', 'issues':[], 'copy_approved':False}
        try:
            trades, fetched = load(base, sid, 'closed_trades')
            chosen=[]
            for t in trades:
                closed=timestamp(t['CloseDate'])
                if start <= closed <= now:
                    gross=num(t['ProfitLoss'])
                    # The API's commission treatment is not verified: use reported P/L
                    # for descriptive win/loss metrics only, never as net returns.
                    chosen.append((closed, gross))
            chosen.sort()
            n=len(chosen)
            item['closed_trades_15d']=n
            if n < MIN_TRADES:
                item['issues'].append('SMALL_SAMPLE_OBSERVATION_ONLY')
            wins=sum(p>0 for _,p in chosen)
            losses=sum(p<0 for _,p in chosen)
            item['wins']=wins
            item['losses']=losses
            item['win_rate_pct']=round(100*wins/n,2) if n else None
            # Shrink win rate toward 50% with 20 pseudo-trades. This helps avoid
            # declaring 5/5 a proven 100% edge.
            item['shrunk_win_rate_pct']=round(100*(wins+10)/(n+20),2)
            gain=sum(max(p,0) for _,p in chosen)
            loss=-sum(min(p,0) for _,p in chosen)
            item['profit_factor_reported']=round(gain/loss,3) if loss else None
            if not loss:
                item['issues'].append('NO_OBSERVED_LOSSES_UNBOUNDED_PF')
            item['reported_pnl_sum']=round(sum(p for _,p in chosen),2)
            # The same number of hits distributed over several weeks is more
            # useful than a single cluster, but recency alone is not proof.
            weeks=len({d.date().isocalendar()[:2] for d,_ in chosen})
            item['active_weeks']=weeks
            item['active_days']=len({d.date() for d,_ in chosen})
            item['recent_last_trade_utc']=chosen[-1][0].isoformat() if chosen else None
            if not chosen or now-chosen[-1][0] > timedelta(days=14):
                item['issues'].append('NO_RECENT_CLOSED_TRADE')
            if n:
                # Explicit research-only score: no unverified capital normalization.
                # Above-average means shrunk win-rate > 50%; require at least
                # two active weeks to avoid single-session streaks.
                score = (item['shrunk_win_rate_pct']-50)*0.7 + min(weeks,8)*2
                item['prodigy_score']=round(score,2)
                meets_gates = (
                    n >= MIN_TRADES
                    and len({d.date() for d, _ in chosen}) >= 3
                    and item['shrunk_win_rate_pct'] > 55
                    and 'NO_RECENT_CLOSED_TRADE' not in item['issues']
                    and item.get('reported_pnl_sum', 0) > 0
                )
                if meets_gates and losses > 0:
                    pf = item.get('profit_factor_reported')
                    meets_gates = pf is not None and pf >= 1
                item['status'] = (
                    'PRODIGY_CANDIDATE_RESEARCH' if meets_gates else 'OBSERVATION'
                )
            else:
                item['prodigy_score']=None
        except (ValueError,TypeError,KeyError,OSError,OverflowError) as exc:
            item['issues'].append('SOURCE_READ_FAILURE')
            item['error_type']=type(exc).__name__
        entries.append(item)
    pearl = [e for e in entries if is_pearl_candidate(e)]
    pearl.sort(key=pearl_sort_key)
    pearl_top = pearl[:PEARL_TOP_N]
    entries.sort(
        key=lambda x: (
            x['status'] != 'PRODIGY_CANDIDATE_RESEARCH',
            *(
                pearl_sort_key(x)
                if x['status'] == 'PRODIGY_CANDIDATE_RESEARCH'
                else (0.0, 0.0, 0.0, 0.0)
            ),
        )
    )
    return {'mode':'PRODIGY_RANK_RESEARCH_ONLY','as_of':now.isoformat(),'window_days':WINDOW_DAYS,
        'score_warning':'Heuristic win-rate screen, not statistical evidence of profit or tradability; costs and cash flows unverified.',
        'providers':entries,'top_10_research':pearl_top, 'copy_approved':[],
        'orders_sent':0,'execution_authorized':False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--raw-dir',default='/app/reports/providers/raw')
    p.add_argument('--output-dir',default='/app/reports/intelligence')
    a=p.parse_args()
    result=calculate(Path(a.raw_dir))
    output=Path(a.output_dir);output.mkdir(parents=True,exist_ok=True)
    (output/'prodigy-top10-latest.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({'mode':result['mode'],'providers':len(result['providers']),
                      'candidates':sum(x['status']=='PRODIGY_CANDIDATE_RESEARCH' for x in result['providers']),
                      'file':str(output/'prodigy-top10-latest.json'),
                      'orders_sent':0,'execution_authorized':False},indent=2))

if __name__=='__main__':main()
