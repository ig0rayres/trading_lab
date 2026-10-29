"""Cross-market, offline-verifiable shadow opportunity screens; NEVER an order signal.

Input JSON: {market, symbol, bars:[{at,close,high,low,volume}, ...],
              quality_verified:boolean, event_reviewed:boolean}
Not a substitute for market/news feeds, corporate-actions handling, or execution.
"""
import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

MARKETS = {'US_EQUITY', 'B3_EQUITY', 'CRYPTO'}
DROP_RADAR = {'US_EQUITY': 5.0, 'B3_EQUITY': 5.0, 'CRYPTO': 8.0}
DROP_EXTREME = {'US_EQUITY': 10.0, 'B3_EQUITY': 10.0, 'CRYPTO': 15.0}

def inspect(item):
    market = item.get('market')
    symbol = item.get('symbol')
    if market not in MARKETS or not isinstance(symbol, str) or not symbol or len(symbol)>28:
        raise ValueError('INVALID_MARKET_OR_SYMBOL')
    bars = item.get('bars')
    if not isinstance(bars, list) or len(bars)<6:
        raise ValueError('INSUFFICIENT_BARS')
    stamp=[]; prices=[]; volumes=[]; highs=[]; lows=[]
    for b in bars:
        at=datetime.fromisoformat(str(b['at']).replace('Z','+00:00'))
        if at.tzinfo is None or at.utcoffset() is None: raise ValueError('UNZONED_TIMESTAMP')
        close=float(b['close']); high=float(b['high']); low=float(b['low']); volume=float(b['volume'])
        if not all(map(math.isfinite,(close,high,low,volume))) or close<=0 or low<=0 or high<close or close<low or volume<0:
            raise ValueError('INVALID_BAR')
        stamp.append(at.astimezone(timezone.utc));prices.append(close);volumes.append(volume);highs.append(high);lows.append(low)
    if any(b<=a for a,b in zip(stamp,stamp[1:])):raise ValueError('UNSORTED_OR_DUPLICATE_BARS')
    # Use the last 5 completed bars; reject stale source data rather than saying 'live'.
    peak=max(prices[-6:-1]);last=prices[-1]
    drawdown_pct=100*(last/peak-1)
    returns=[math.log(prices[i]/prices[i-1]) for i in range(1,len(prices))]
    vol_pct=100*pstdev(returns[-min(20,len(returns)):])
    fall=abs(drawdown_pct)
    trigger=fall>=DROP_RADAR[market]
    # Evidence of rebound is recorded separately from price drawdown.
    last_rebound=last>prices[-2] and last> (highs[-2]+lows[-2])/2
    flags=[]
    if not item.get('quality_verified'):flags.append('QUALITY_UNVERIFIED')
    if not item.get('event_reviewed'):flags.append('CATALYST_NOT_REVIEWED')
    if not last_rebound:flags.append('REVERSAL_UNCONFIRMED')
    if vol_pct==0:flags.append('VOLATILITY_UNAVAILABLE')
    if not trigger:flags.append('DROP_BELOW_RADAR_THRESHOLD')
    return {'market':market,'symbol':symbol,'strategy':'TA_BARATO_DEMAIS','mode':'SHADOW_ONLY',
            'as_of':stamp[-1].isoformat(),'drop_pct_from_previous_5_bar_peak':round(fall,3),
            'return_volatility_pct':round(vol_pct,3),'extreme_drop':fall>=DROP_EXTREME[market],
            'radar_candidate':trigger,'rebound_confirmation':last_rebound,
            'issues':flags,'paper_approved':False,'orders_sent':0}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output')
    args=parser.parse_args()
    inp=Path(args.input); obj=json.loads(inp.read_text())
    rows=obj if isinstance(obj,list) else [obj]
    output={'schema_version':'opportunity-v4','mode':'SHADOW_ONLY','opportunities':[inspect(x) for x in rows], 'orders_sent':0}
    if args.output:
        path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
