import json
from datetime import datetime, timezone
from v4_shadow_audit import append_evaluation, report, verify


def intent(signal='a'):
    return {'event':'PAPER_ENTRY_REQUESTED_NOT_FILLED','status':'PENDING_VERIFIED_MARKET_FILL',
            'market':'B3_EQUITY','strategy_id':'cheap','signal_id':signal,
            'at_utc':'2026-10-29T12:00:00+00:00','entry_brl':'100','stop_brl':'95','quantity':'2'}


def bars(close='106'):
    return [{'at_utc':'2026-10-29T13:00:00+00:00','complete':True,'verified':True,
             'open_brl':'100','high_brl':'108','low_brl':'99','close_brl':close}]


def test_success_and_report(tmp_path):
    path=tmp_path/'ledger.jsonl'
    result=append_evaluation(intent(),bars(),target_brl='105',ledger=path)
    assert result['status']=='SHADOW_EVALUATION_RECORDED'
    assert verify(path)['valid']
    stats=report(path)
    assert stats['broker_fills']==0
    assert stats['outcomes']['HYPOTHETICAL_TARGET']==1
    assert stats['hypothetical_closed_net_pnl_brl']=='10'


def test_duplicate_fail_closed(tmp_path):
    path=tmp_path/'ledger.jsonl'
    append_evaluation(intent(),bars(),target_brl='105',ledger=path)
    assert append_evaluation(intent(),bars(),target_brl='105',ledger=path)['reason']=='ALREADY_EVALUATED'
    assert verify(path)['events']==1


def test_corruption_blocks_append(tmp_path):
    path=tmp_path/'ledger.jsonl'
    append_evaluation(intent(),bars(),target_brl='105',ledger=path)
    line=path.read_text()
    path.write_text(line.replace('HYPOTHETICAL_TARGET','HYPOTHETICAL_STOP'))
    assert not verify(path)['valid']
    assert append_evaluation(intent('b'),bars(),target_brl='105',ledger=path)['status']=='BLOCKED'
    assert report(path)['integrity']=='FAILED'


def test_invalid_and_live_refused(tmp_path,monkeypatch):
    path=tmp_path/'ledger.jsonl'
    assert append_evaluation(intent(),[dict(bars()[0],verified=False)],target_brl='105',ledger=path)['status']=='BLOCKED'
    monkeypatch.setenv('LIVE_TRADING_ENABLED','true')
    assert append_evaluation(intent(),bars(),target_brl='105',ledger=path)['reason']=='LIVE_TRADING_NOT_DISABLED'
    assert not path.exists()


def test_two_events_hash_chain(tmp_path):
    path=tmp_path/'ledger.jsonl'
    for sig in ('a','b'):
        assert append_evaluation(intent(sig),bars(),target_brl='105',ledger=path)['status']=='SHADOW_EVALUATION_RECORDED'
    first,second=map(json.loads,path.read_text().splitlines())
    assert second['previous_hash']==first['hash']
    assert verify(path)['events']==2


def test_missing_file_is_explicitly_empty(tmp_path):
    state=report(tmp_path/'missing.jsonl')
    assert state['events']==0 and state['broker_fills']==0
