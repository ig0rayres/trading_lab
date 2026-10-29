"""Ten completed-session technical replay. Never reconstruct historical news/facts from today's feed."""
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from swing_radar import DEFAULT_SYMBOLS, yahoo_daily, technical


def replay(price_series, days=10):
    if not 1 <= days <= 40:
        raise ValueError('days must be 1..40')
    if not price_series or any(len(v) < days + 65 for v in price_series.values()):
        raise ValueError('Insufficient history for causal replay')
    common = set.intersection(*(set(bar['day'] for bar in series) for series in price_series.values()))
    sessions = sorted(common)[-days-1:-1]
    if len(sessions) != days:
        raise ValueError('Insufficient common completed sessions')
    by_symbol = {s:{b['day']:b for b in bars} for s,bars in price_series.items()}
    results=[]
    for i, day in enumerate(sessions):
        rows=[]
        for symbol,bars in price_series.items():
            history=[bar for bar in bars if bar['day']<=day]
            if len(history)<65:
                raise ValueError('Insufficient past candles')
            indicator=technical(history, today=datetime.fromisoformat(day).date())
            # Strictly research-only: no corporate fundamentals or verified point-in-time news.
            # NO_TRADE is mandatory, even when the technical setup passes.
            close=by_symbol[symbol][day]['close']
            future_days=[d for d in sorted(by_symbol[symbol]) if d>day]
            future={}
            for horizon in (1,3,5,10):
                if len(future_days)>=horizon:
                    future[str(horizon)]=round((by_symbol[symbol][future_days[horizon-1]]['close']/close-1)*100,3)
                else:
                    future[str(horizon)]=None
            technical_score=(3 if indicator['trend']=='UP' else 0)+(2 if 45<=indicator['rsi14']<=65 else 0)+(2 if indicator['volume_ratio20']>=1 else 0)
            blockers=[]
            if indicator['trend']!='UP': blockers.append('NO_CONFIRMED_UPTREND')
            if indicator['volume_ratio20']<0.8: blockers.append('WEAK_VOLUME_CONFIRMATION')
            if not 40<=indicator['rsi14']<=70: blockers.append('MOMENTUM_OUTSIDE_CONSERVATIVE_RANGE')
            blockers.extend(['HISTORICAL_NEWS_NOT_VERIFIED','HISTORICAL_FUNDAMENTALS_NOT_VERIFIED','NO_VALIDATED_EDGE'])
            rows.append({'symbol':symbol,'technical_score':technical_score,'trend':indicator['trend'],
                         'rsi14':indicator['rsi14'],'volume_ratio20':indicator['volume_ratio20'],
                         'decision':'NO_TRADE','blockers':blockers,'close':round(close,4),
                         'forward_returns_pct_descriptive_only':future})
        rows.sort(key=lambda r:(len(r['blockers']),-r['technical_score'],r['symbol']))
        results.append({'session':day,'ranked_candidates':rows})
    symbols=sorted(price_series)
    return {'mode':'CAUSAL_TECHNICAL_REPLAY_NO_ORDERS','sessions':days,
            'created_at_utc':datetime.now(timezone.utc).isoformat(),
            'universe':symbols,'orders_sent':0,'simulated_trades':0,'realized_pnl_usd':0,
            'decisions':results,'limitations':[
                'Not a point-in-time replay of news, SEC filings or full v1.7 ranking.',
                'No historical trade is opened: all decisions are NO_TRADE.',
                'Future returns are descriptive diagnostics, never used to rank past candidates.',
                'Historical candles come from an unofficial Yahoo endpoint; may be revised, split-affected or incomplete.',
                'No transaction costs, intraday path, fill model, stop execution or P&L modeled.',
                'Ten sessions is an insufficient sample to establish an edge.',
                'Latest available daily bar may be incomplete; excluded from the decision window.'
            ]}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--days',type=int,default=10)
    p.add_argument('--symbols',default=DEFAULT_SYMBOLS)
    p.add_argument('--output',default='/app/reports/replay/last-10-sessions.json')
    a=p.parse_args()
    if os.getenv('LIVE_TRADING_ENABLED','false').lower()!='false':
        raise SystemExit('Live trading must remain disabled')
    from datetime import datetime
    from zoneinfo import ZoneInfo
    now=datetime.now(ZoneInfo('America/New_York'))
    symbols=list(dict.fromkeys(x.strip().upper() for x in a.symbols.split(',') if x.strip()))
    if not symbols or len(symbols)>30 or a.days<1 or a.days>40: raise SystemExit('Invalid symbols/days')
    prices={}
    for symbol in symbols:
        bars=yahoo_daily(symbol)
        # The ongoing day is never a completed session; after 16:15 ET allow today's daily bar.
        if bars and bars[-1]['day']>=now.date().isoformat() and (now.hour,now.minute)<(16,15):
            bars=[b for b in bars if b['day']<now.date().isoformat()]
        prices[symbol]=bars
    report=replay(prices,a.days)
    dest=Path(a.output); dest.parent.mkdir(parents=True,exist_ok=True)
    temp=dest.with_suffix('.tmp');temp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');temp.replace(dest)
    print(json.dumps({'mode':report['mode'],'sessions':a.days,'assets':len(symbols),'orders_sent':0,
                      'output':str(dest),'disclaimer':'Technical replay only, NO_TRADE, no verified historical news/fundamentals'}))

if __name__=='__main__':main()
