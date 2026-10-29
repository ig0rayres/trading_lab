#!/usr/bin/env python3
"""Research-only multi-session ORB replay calling ORIGINAL entry/exit/budget/risk.

Static symbol lists: no same-day scanner leakage. Still subject to historical
universe/survivorship bias. Yahoo free 5m bars usually cover at most ~60 days.
No orders, broker code, or portfolio performance; every signal is audited
against an illustrative fresh budget independently.
"""
import argparse
import csv
import datetime as dt
from decimal import Decimal
import json
import math
from pathlib import Path
import sys
import time
from zoneinfo import ZoneInfo

from original import load_original

NY = ZoneInfo('America/New_York')
UTC = dt.timezone.utc
FIELDS = ['symbol','date','signal_at','entry_at','or_high','or_low','entry_raw','entry_fill','stop',
          'target','target_r','exit_at','exit_reason','exit_fill','pnl_per_share','net_r','net_pct',
          'budget_qty','risk_verdict','risk_reasons','upstream_commit']


def dstr(x):
    return str(x) if x is not None else ''


def parse_symbol_list(args):
    items = args.symbols.split(',') if args.symbols else (['TSLA','NVDA','AMD'] if args.symbols is None and not args.symbols_file else [])
    if args.symbols_file:
        p = Path(args.symbols_file)
        if not p.is_file():
            raise ValueError('SYMBOLS_FILE_MISSING: %s' % p)
        items.extend(p.read_text().replace(',', '\n').splitlines())
    result=[]
    for raw in items:
        sym = raw.strip().upper()
        if not sym or sym.startswith('#'):
            continue
        if not all(c.isascii() and (c.isupper() or c.isdigit() or c in '.-') for c in sym) or len(sym)>12:
            raise ValueError('INVALID_SYMBOL: '+sym)
        if sym not in result: result.append(sym)
    if not result:
        raise ValueError('Provide --symbols TSLA,NVDA,AMD or --symbols-file FILE; NEVER use a future-selected watchlist')
    if len(result) > args.max_symbols:
        raise ValueError('Too many symbols; max %d (use --max-symbols to explicitly raise)' % args.max_symbols)
    return result


def orig_years(original):
    return set(original.entry.CALENDAR_YEARS)


def dates_for(args, today, original):
    end = dt.date.fromisoformat(args.to_date) if args.to_date else today - dt.timedelta(days=1)
    start = dt.date.fromisoformat(args.from_date) if args.from_date else end - dt.timedelta(days=args.days-1)
    if start > end: raise ValueError('--from cannot be after --to')
    if end >= today:
        raise ValueError('HISTORICAL_ONLY: --to must precede the current NY date. Use orb-batch --intraday for today.')
    if any(date.year not in orig_years(original) for date in (start,end)):
        raise ValueError('CALENDAR_NOT_VALIDATED: original NYSE calendar covers only %s' % sorted(orig_years(original)))
    if not args.offline_dir and (today-start).days > 58:
        raise ValueError('YAHOO_5M_LIMIT: start exceeds about 58 days from today; use a shorter range or --offline-dir')
    if not args.offline_dir and (end-start).days > 57:
        raise ValueError('YAHOO_5M_LIMIT: max 58 calendar days in one retrieval; use smaller windows')
    dates=[]
    for days in range((end-start).days+1):
        date=start+dt.timedelta(days=days)
        if original.entry.session(date) is not None: dates.append(date)
    if not dates: raise ValueError('NO_TRADING_SESSIONS')
    return dates


def parse_strict_chart(orig, raw, sym):
    # Original parser is authoritative, but it intentionally substitutes the
    # close for a missing OHLC. For research we instead reject those slots.
    parsed=orig.entry.parse_chart(raw,sym)
    source=json.loads(raw)
    result=(source.get('chart') or {}).get('result') or []
    if not result:raise ValueError('YAHOO_EMPTY_RESULT')
    obj=result[0]
    ticks=obj.get('timestamp') or []
    q=((obj.get('indicators') or {}).get('quote') or [{}])[0] or {}
    strict=set()
    for i,t in enumerate(ticks):
        if t is not None and all(i<len(q.get(k) or []) and q[k][i] is not None
                                 for k in ('open','high','low','close')):
            strict.add(int(t))
    parsed['bars']=[b for b in parsed['bars'] if b['t'] in strict]
    if parsed['symbol'] != orig.entry.yahoo_symbol(sym):
        raise ValueError('YAHOO_WRONG_SYMBOL: '+parsed['symbol'])
    return parsed


def get_chart(orig, sym, dates, today, cache_dir, offline_dir, pause, refresh=False):
    if offline_dir:
        p=orig.entry.offline_file(offline_dir,sym)
        raw=orig.entry.read_text(p)
        return parse_strict_chart(orig,raw,sym)
    # Original Yahoo HTTP, symbol adapter and JSON parser; only storage is ours.
    # Longest required range is selected by the original chart_range() function.
    rng = orig.entry.chart_range(dates[0], today, '5m')
    cache_dir.mkdir(parents=True,exist_ok=True)
    safe = orig.entry.yahoo_symbol(sym)
    cache = cache_dir / ('%s-%s-%s.json' % (safe, today.isoformat(), rng))
    if cache.exists() and not refresh:
        raw = cache.read_text(encoding='utf-8')
    else:
        raw = orig.entry.yahoo_get(orig.entry.chart_path(sym, rng, '5m'))
        # Only cache validated JSON. Atomic replacement protects previous run.
        parsed = parse_strict_chart(orig, raw, sym)
        if not parsed['bars']: raise ValueError('YAHOO_EMPTY_CHART')
        temp=cache.with_suffix('.tmp')
        temp.write_text(raw,encoding='utf-8')
        temp.replace(cache)
        if pause:time.sleep(pause)
    chart=parse_strict_chart(orig,raw,sym)
    if chart['symbol'] != orig.entry.yahoo_symbol(sym):
        raise ValueError('YAHOO_WRONG_SYMBOL: '+chart['symbol'])
    gran=chart.get('meta',{}).get('dataGranularity')
    if gran and gran != '5m':raise ValueError('YAHOO_WRONG_INTERVAL: '+str(gran))
    return chart


def session_bars(orig, chart, date):
    times = orig.entry.session(date)
    if times is None: return None, 'MARKET_CLOSED'
    open_at, close_at = times
    o=dt.datetime.combine(date,open_at,NY)
    c=dt.datetime.combine(date,close_at,NY)
    expected = int((c-o).total_seconds()//300)
    grid={}
    for raw in chart['bars']:
        t = dt.datetime.fromtimestamp(raw['t'],NY)
        if t.date()!=date or t < o or t >= c: continue
        if t.second or t.microsecond or (t.minute%5):continue
        if t in grid:return None, 'DUPLICATE_BAR'
        vals=[raw[k] for k in ('o','h','l','c')]
        if any(not math.isfinite(float(v)) or float(v)<=0 for v in vals):return None,'BAD_OHLC'
        op,hi,lo,cl=map(float,vals)
        if lo>min(op,cl) or hi<max(op,cl) or hi<lo:return None,'INVALID_OHLC'
        grid[t]={'start':t, 'end':t+dt.timedelta(minutes=5), 'open':op, 'high':hi, 'low':lo,
                 'close':cl,'volume':int(raw.get('v',0))}
    if len(grid)!=expected:return None,'INCOMPLETE_SESSION:%d/%d'%(len(grid),expected)
    bars=[]
    for index in range(expected):
        t=o+dt.timedelta(minutes=5*index)
        if t not in grid:return None,'MISSING_SLOT:'+t.isoformat()
        bars.append(grid[t])
    return bars,None


def simulate_day(orig, chart, bars, date, target_r, fees_bps=5.,slip_bps=5.,
                 budget_usd=5000., stop_rule='or-mid', setup='orb', level=None, min_volume_x=None):
    """Single-strategy independent per-share replay. Original modules decide
    entry trigger, stop/target, position size and risk audit.
    All bars exist as a completed day; entry.evaluate sees only this session
    and chooses the FIRST eligible completed breakout candle.
    """
    session=orig.entry.session(date)
    now_local=dt.datetime.combine(date,session[1],NY)
    now_utc=now_local.astimezone(UTC).replace(tzinfo=None)
    result=orig.entry.evaluate(chart,now_utc,setup=setup,or_minutes=15,interval='5m',level=level,min_volume_x=min_volume_x)
    if result['status']!='triggered':return None
    trigger=result['trigger']
    local_time=dt.time.fromisoformat(trigger['close_time'])
    entered_at=dt.datetime.combine(date,local_time,NY)
    idx=next((i for i,b in enumerate(bars) if b['start']==entered_at),None)
    if idx is None:raise ValueError('NO_NEXT_BAR_AT:'+trigger['close_time'])
    opening=result.get('opening_range') or {}
    if not opening.get('complete') or opening.get('bars')!=3:
        raise ValueError('INVALID_OPENING_RANGE')
    raw=Decimal(str(bars[idx]['open']))
    buy_fill=raw*(Decimal('1')+Decimal(str(slip_bps))/Decimal('10000'))
    sr, sp=orig.exit.parse_stop(stop_rule)
    if sr not in ('or_mid','or_low','pct'):raise ValueError('UNSUPPORTED_STOP_RULE')
    tr,tp=orig.exit.parse_target(str(target_r)+'R')
    plan=orig.exit.compute(buy_fill,sr,sp,tr,tp,or_high=opening['high'],or_low=opening['low'])
    risk=Decimal(str(plan['entry']))-Decimal(str(plan['stop']))
    flat=dt.datetime.combine(date,session[1],NY)-dt.timedelta(minutes=5)
    stop=Decimal(str(plan['stop'])); target=Decimal(str(plan['target']))
    reason=None;ex_raw=None;ex_at=None
    for b in bars[idx:]:
        if b['start']>=flat:break
        op=Decimal(str(b['open']));hi=Decimal(str(b['high']));lo=Decimal(str(b['low']))
        if op<=stop:
            reason='stop_gap';ex_raw=op;ex_at=b['start'];break
        if lo<=stop:
            reason='stop';ex_raw=stop;ex_at=b['end'];break
        if hi>=target:
            reason='target';ex_raw=target;ex_at=b['end'];break
        if b['end']==flat:
            reason='flat';ex_raw=Decimal(str(b['close']));ex_at=flat;break
    if reason is None:raise ValueError('MISSING_FINAL_EXIT')
    sell_fill=ex_raw*(Decimal('1')-Decimal(str(slip_bps))/Decimal('10000'))
    cost=Decimal(str(fees_bps))/Decimal('10000')*(buy_fill+sell_fill)
    pnl=sell_fill-buy_fill-cost
    # We intentionally evaluate the plan at the original module's cent precision.
    # The actual slipped fill is kept at full precision for costs and PnL.
    doc={'symbol':chart['symbol'],'side':'buy','date':date.isoformat(),'setup':setup,
         'entry_time':entered_at.strftime('%H:%M'),'entry':str(plan['entry']),
         'stop':str(stop),'target':str(target),'flat_by':flat.strftime('%H:%M')}
    cfg={'budget':budget_usd,'paper':True,'allow_margin':False,'allow_short':False,
         'allow_options':False,'max_loss_per_trade_usd':min(50.,budget_usd*.01),
         'max_daily_loss_usd':min(150.,budget_usd*.03),
         'max_order_usd':budget_usd,'max_position_pct':75,'cash_buffer_pct':10,
         'min_reward_risk':1.0,'max_trades_per_day':3,'max_orders_per_day':10}
    sized=orig.budget.size_trade(doc,cfg,today=date.isoformat())
    order=orig.budget.bracket_order(sized)
    if order is None:
        verdict='BLOCK_SIZE';reasons=[sized.get('refusal') or 'no size']
    else:
        audit=orig.risk.check([order],cfg,today=date.isoformat(),
                               now=entered_at.astimezone(UTC).replace(tzinfo=None))
        verdict=audit['results'][0]['verdict']
        reasons=audit['results'][0]['reasons']
    return dict(symbol=chart['symbol'],date=date.isoformat(),
        signal_at=entered_at.isoformat(),entry_at=entered_at.isoformat(),
        or_high=opening['high'],or_low=opening['low'],entry_raw=float(raw),
        entry_fill=round(float(buy_fill),6),stop=float(stop),target=float(target),
        target_r=target_r,exit_at=ex_at.isoformat(),exit_reason=reason,
        exit_fill=round(float(sell_fill),6),pnl_per_share=round(float(pnl),6),
        net_r=round(float(pnl/risk),6),net_pct=round(100*float(pnl/buy_fill),5),
        budget_qty=int(sized['qty']),risk_verdict=verdict,
        risk_reasons='; '.join(reasons),upstream_commit=orig.commit)


def metrics(rows):
    count=len(rows)
    if not count:return {'evaluations':0,'wins':0,'win_rate_pct':None,'mean_net_r':None,'profit_factor':None,'total_net_r':0}
    values=[float(x['net_r']) for x in rows]
    gross_win=sum(v for v in values if v>0)
    gross_loss=-sum(v for v in values if v<0)
    return {'evaluations':count,'wins':sum(v>0 for v in values),
            'win_rate_pct':round(100*sum(v>0 for v in values)/count,2),
            'mean_net_r':round(sum(values)/count,5),
            'profit_factor':round(gross_win/gross_loss,4) if gross_loss else None,
            'total_net_r':round(sum(values),5),
            'risk_pass':sum(x['risk_verdict']=='PASS' for x in rows),
            'risk_blocked':sum(x['risk_verdict']!='PASS' for x in rows)}


def main(argv=None):
    ap=argparse.ArgumentParser(description='Multi-session ORB research using upstream original modules')
    ap.add_argument('--from',dest='from_date')
    ap.add_argument('--to',dest='to_date')
    ap.add_argument('--days',type=int,default=30,help='Calendar-day span; ends yesterday by default')
    ap.add_argument('--symbols',default=None,help='Static research universe; never a same-day scan')
    ap.add_argument('--symbols-file',help='One predeclared symbol per line; replaces future-selected watchlists')
    ap.add_argument('--max-symbols',type=int,default=30)
    ap.add_argument('--offline-dir',help='Offline Yahoo chart JSONs named SYMBOL.json (reproducible)')
    ap.add_argument('--output',help='Result folder. Default: /app/reports/history/RANGE')
    ap.add_argument('--repo',help='Original GitHub repo path, defaults to vendor mount')
    ap.add_argument('--stop',choices=['or-mid','or-low'],default='or-mid')
    ap.add_argument('--fee-bps',type=float,default=5.)
    ap.add_argument('--slippage-bps',type=float,default=5.)
    ap.add_argument('--budget-usd',type=float,default=5000.)
    ap.add_argument('--pause',type=float,default=.3)
    ap.add_argument('--refresh',action='store_true',help='Refetch raw historical chart instead of cache')
    args=ap.parse_args(argv)
    if args.days<1 or (args.days>58 and not args.offline_dir) or args.max_symbols<1 or args.budget_usd<=0 or any(v<0 for v in [args.fee_bps,args.slippage_bps,args.pause]):
        ap.error('Invalid days, limits, budget or costs')
    try:
        orig=load_original(args.repo)
        today=dt.datetime.now(NY).date()
        dates=dates_for(args,today,orig)
        symbols=parse_symbol_list(args)
    except (ValueError,RuntimeError) as e:
        ap.error(str(e))
    out=Path(args.output or ('/app/reports/history/%s_to_%s' % (dates[0],dates[-1])))
    out.mkdir(parents=True,exist_ok=True)
    rows=[];errors=[];days_per_sym={};signals=0
    for idx,symbol in enumerate(symbols,1):
        try:
            chart=get_chart(orig,symbol,dates,today,out/'cache',args.offline_dir,args.pause,args.refresh)
        except Exception as e:
            errors.append({'symbol':symbol,'date':'*','error':'FETCH_OR_PARSE:'+str(e)})
            print('Processed %d/%d symbols (fetch error)'%(idx,len(symbols)),flush=True)
            continue
        days_per_sym[symbol]=0
        for date in dates:
            bars,error=session_bars(orig,chart,date)
            if error:
                errors.append({'symbol':symbol,'date':date.isoformat(),'error':error})
                continue
            days_per_sym[symbol]+=1
            # All target variants share one signal. Every choice is made by the
            # upstream original modules. No current watchlist is consulted.
            for target_r in (1,2):
                try:
                    row=simulate_day(orig,chart,bars,date,target_r,args.fee_bps,
                        args.slippage_bps,args.budget_usd,args.stop)
                    if row:rows.append(row)
                except Exception as e:
                    errors.append({'symbol':symbol,'date':date.isoformat(),'target_r':target_r,'error':'REPLAY:'+str(e)})
        print('Processed %d/%d symbols'%(idx,len(symbols)),flush=True)
    # A skipped 1R or 2R for the same signal is not counted as a full paired trade.
    pairs={}
    for r in rows:
        pairs.setdefault((r['symbol'],r['date']),set()).add(r['target_r'])
    incomplete={k for k,p in pairs.items() if p!={1,2}}
    if incomplete:
        errors.extend({'symbol':s,'date':d,'error':'INCOMPLETE_TARGET_PAIR'} for s,d in sorted(incomplete))
        rows=[r for r in rows if (r['symbol'],r['date']) not in incomplete]
    signals=len({(r['symbol'],r['date']) for r in rows})
    with (out/'trades.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
    (out/'errors.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False))
    cut=dates[max(0,int(len(dates)*.7)-1)]
    by={}
    for r in (1,2):
        subset=[x for x in rows if x['target_r']==r]
        by[str(r)+'R']={'all':metrics(subset),
                        'earlier_sessions':metrics([x for x in subset if x['date']<=cut.isoformat()]),
                        'later_sessions':metrics([x for x in subset if x['date']>cut.isoformat()])}
    summary={'status':'EXPLORATORY_HISTORICAL_NOT_VALIDATED','source':'ORIGINAL_UPSTREAM_ENTRY_EXIT_BUDGET_RISK',
             'upstream_repo':orig.path,'upstream_commit':orig.commit,'start':dates[0].isoformat(),
             'end':dates[-1].isoformat(),'session_dates':len(dates),'symbols_requested':len(symbols),
             'symbol_sessions_complete':sum(days_per_sym.values()),'signals_with_both_targets':signals,
             'errors':len(errors),'strategies':by,
             'assumptions':{'stop':args.stop,'entry':'next 5m bar open after first closed breakout',
             'flat':'5 minutes before official session close','both_touched':'stop first',
             'fees_bps_per_side':args.fee_bps,'slippage_bps_per_side':args.slippage_bps,
             'budget_usd_for_independent_risk_audit':args.budget_usd},
             'warnings':['No broker connection or orders; results are per-share independent hypotheticals.',
             'Static modern ticker universe has survivorship and membership biases; not an institutional point-in-time universe.',
             'Yahoo unofficial 5m historical quotes can be inaccurate; same-bar ordering, spread and fills are unknown.',
             'No joint portfolio position sizing or concurrency simulation; the upstream risk module audits each signal independently.',
             'Chronological segments are descriptive, not held-out validation if parameters were chosen after examining the period.',
             'No demonstrated edge or authorization for live trading.']}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print('Report: '+str(out))
    return 0 if signals else 2


if __name__=='__main__':
    sys.exit(main())
