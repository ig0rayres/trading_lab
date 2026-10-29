import pytest
from v4_shadow_marks import evaluate_shadow

INTENT = {'event': 'PAPER_ENTRY_REQUESTED_NOT_FILLED', 'status': 'PENDING_VERIFIED_MARKET_FILL',
          'at_utc': '2026-10-29T13:00:00+00:00', 'entry_brl': '100', 'stop_brl': '95',
          'quantity': '2', 'signal_id': 'example-1'}

def bar(ts='2026-10-29T14:00:00+00:00', op='100', high='104', low='99', close='102', **kw):
    return {'at_utc': ts, 'open_brl': op, 'high_brl': high, 'low_brl': low,
            'close_brl': close, 'verified': True, 'complete': True, **kw}

def test_open_not_fill():
    x=evaluate_shadow(INTENT,[bar()],target_brl='110')
    assert x['status']=='HYPOTHETICAL_OPEN' and x['broker_filled'] is False

def test_target_net_fees():
    x=evaluate_shadow(INTENT,[bar(high='111')],target_brl='110',fee_brl='2',slippage_brl='1')
    assert x['hypothetical_net_pnl_brl']=='16' and x['status']=='HYPOTHETICAL_TARGET'

def test_stop_first_if_ambiguous():
    x=evaluate_shadow(INTENT,[bar(high='111',low='94')],target_brl='110')
    assert x['status']=='HYPOTHETICAL_STOP' and x['hypothetical_net_pnl_brl']=='-10'

def test_gap_stop():
    x=evaluate_shadow(INTENT,[bar(op='92',high='97',low='91',close='93')],target_brl='110')
    assert x['hypothetical_net_pnl_brl']=='-16'

@pytest.mark.parametrize('bars',[
    [bar(complete=False)], [bar(verified=False)], [bar(ts='2026-10-29T12:00:00+00:00')],
    [bar(high='99')], [bar(),bar(ts='2026-10-29T13:30:00+00:00')],
    [bar(ts='2026-10-29T14:00:00')],
])
def test_reject_invalid_bars(bars):
    with pytest.raises(ValueError): evaluate_shadow(INTENT,bars,target_brl='110')

def test_pending():
    assert evaluate_shadow(INTENT,[],target_brl='110')['status']=='HYPOTHETICAL_PENDING'

def test_reject_untrusted_intent():
    with pytest.raises(ValueError): evaluate_shadow({**INTENT,'event':'BROKER_FILLED'},[],target_brl='110')
