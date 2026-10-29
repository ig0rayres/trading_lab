#!/usr/bin/env python3
"""Run deterministic parity/integration checks against the REAL upstream code.

No GitHub fetch, no trading, no network. Upstream modules loaded from /app/vendor.
"""
import datetime as dt
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo
from original import load_original
from history import session_bars, simulate_day

NY=ZoneInfo('America/New_York')


def fixture_chart(date=dt.date(2026,10,19)):
    start=dt.datetime.combine(date,dt.time(9,30),NY)
    bars=[]
    for i in range(78):
        stamp=start+dt.timedelta(minutes=5*i)
        op=100.0
        high=101.0
        low=99.0
        close=100.0
        if i==3:
            op,high,low,close=100.2,102.2,100.0,102.0  # ORB 9:50 trigger
        if i>=4:
            op,high,low,close=102.5,103.2,102.1,102.8
        if i==7:
            high=110.0  # unambiguous target for 1R and 2R
        bars.append({'t':int(stamp.timestamp()),'o':op,'h':high,'l':low,'c':close,'v':3000})
    return {'symbol':'TEST','meta':{'symbol':'TEST','dataGranularity':'5m'},
            'prev_close':100.0,'data_time':int((start+dt.timedelta(minutes=390)).timestamp()),'bars':bars}


def verify(repo=None):
    orig=load_original(repo)
    ch=fixture_chart()
    date=dt.date(2026,10,19)
    bars,err=session_bars(orig,ch,date)
    assert not err and len(bars)==78,(err,len(bars or []))
    clock=dt.datetime(2026,10,19,16,0,tzinfo=NY).astimezone(dt.timezone.utc).replace(tzinfo=None)
    entry=orig.entry.evaluate(ch,clock,setup='orb',or_minutes=15,interval='5m')
    assert entry['status']=='triggered',entry['status']
    assert entry['trigger']['close_time']=='09:50',entry['trigger']
    # The trigger must be observable already at 09:50, BEFORE future candles.
    early_clock=dt.datetime(2026,10,19,9,50,tzinfo=NY).astimezone(dt.timezone.utc).replace(tzinfo=None)
    earlier=orig.entry.evaluate(ch,early_clock,setup='orb',or_minutes=15,interval='5m')
    assert earlier['status']=='triggered' and earlier['trigger']==entry['trigger'],(earlier,entry)
    # Scanner must return the exact same first trigger and OR range.
    scanner_bars=[{'start':b['start'].replace(tzinfo=None),'h':b['high'],
                   'l':b['low'],'c':b['close'],'v':b['volume']} for b in bars]
    scan=orig.scanner.orb_hit(scanner_bars,3)
    assert scan is not None
    assert scan['bar_start']=='09:45' and scan['price']==entry['trigger']['price'],scan
    assert scan['or_high']==entry['opening_range']['high']
    for mult in (1,2):
        trade=simulate_day(orig,ch,bars,date,mult,fees_bps=5,slip_bps=5)
        assert trade['exit_reason']=='target',trade
        assert trade['net_r']>0,trade
        assert trade['risk_verdict']=='PASS',trade
        assert trade['budget_qty']>0,trade
    # Confirm a break of original stop/target setup blocks a trade rather than
    # silently falling back to a local substitute.
    try:
        orig.exit.compute(100,'or_mid',None,'r',orig.exit.D(1),or_high=101,or_low=101)
    except orig.exit.PlanError:
        pass
    else:
        raise AssertionError('Original exit.compute refused no invalid OR')
    return {'status':'PASS','source':'ACTUAL_ORIGINAL_MODULES','upstream_commit':orig.commit,
            'modules':['trader-entry','trader-exit','trader-budget','trader-risk','trader-scanner'],
            'checks':['first closed-bar entry','scanner/entry parity','1R/2R target',
                      'sizing and risk PASS','invalid plan rejection'],
            'live_orders_enabled':False}


if __name__=='__main__':
    try:
        out=verify(sys.argv[1] if len(sys.argv)>1 else None)
        print(json.dumps(out,indent=2))
    except Exception as e:
        print('ORIGINAL_INTEGRATION_FAILED:',type(e).__name__,str(e),file=sys.stderr)
        sys.exit(2)
