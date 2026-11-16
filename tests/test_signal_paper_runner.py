import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src import signal_paper_runner as x
from src.demo_broker_adapters import G_MKT_ADAPTER_PATH_ALPACA_PAPER
from src.signal_copy import sign

ALPACA_PAPER_HOST = 'https://paper-api.alpaca.markets'

class PaperRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ledger=str(Path(self.tmp.name)/'journal.jsonl')
        self.env={'LIVE_TRADING_ENABLED':'false','ALPACA_PAPER_TRADE':'true',
                  'ALPACA_BASE_URL':'https://paper-api.alpaca.markets',
                  'ALPACA_API_KEY':'test','ALPACA_SECRET_KEY':'test',
                  'USD_BRL_REFERENCE':'5','SIGNAL_COPY_SECRET':'x'*32}
        self.signal={'provider':'provider_1','signal_id':'signal_12345',
                     'symbol':'AAPL','side':'buy','asset_class':'us_equity',
                     'sent_at_utc':datetime.now(timezone.utc).isoformat(),
                     'entry':100,'stop':99,'target':102,'quantity':1,'ttl_seconds':60}
        self.signal['provider_signature']=sign(self.signal,self.env['SIGNAL_COPY_SECRET'])
    def test_preview_does_not_call_broker(self):
        def fail(*a,**k): raise AssertionError('broker called')
        r=x.run(self.signal,self.env,self.ledger,broker_get=fail,broker_post=fail)
        self.assertEqual(r['status'],'PREVIEW_ONLY')
        self.assertFalse(Path(self.ledger).exists())
    def test_bad_signature_blocked(self):
        self.signal['provider_signature']='bad'
        self.assertEqual(x.run(self.signal,self.env,self.ledger)['status'],'BLOCKED')
    def test_auto_mode_requires_attestation(self):
        self.env.update(PAPER_SIGNAL_AUTO_ENABLED='true',PAPER_EXECUTION_ENABLED='true')
        self.assertEqual(x.run(self.signal,self.env,self.ledger)['status'],'BLOCKED')
    def test_unknown_broker_state_blocks_retry(self):
        self.env.update(PAPER_SIGNAL_AUTO_ENABLED='true',PAPER_EXECUTION_ENABLED='true',
                        PAPER_SIGNAL_ACCOUNT_ACK='I_AUTHORIZE_ALPACA_PAPER_ONLY',PAPER_DAILY_RISK_CONFIRMED='true')
        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status':'ACTIVE','currency':'USD','trading_blocked':False,'cash':'2000','equity':'2000'}
            return []
        snapshot=Path(self.tmp.name)/'risk.json'
        snapshot.write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),
            'alpaca_positions_count':0,'alpaca_open_orders_count':0,'complete':True,
            'daily_pnl_verified':True,'weekly_pnl_verified':True,'broker_reconciled':True,
            'positions':[],'daily_pnl_brl':'0','weekly_pnl_brl':'0',
            'available_cash_brl':'10000','has_pending_orders':False}))
        self.env['V4_RISK_SNAPSHOT_FILE']=str(snapshot)
        def broken(*a): raise TimeoutError()
        first=x.run(self.signal,self.env,self.ledger,broker_get=getter,broker_post=broken)
        self.assertEqual(first['status'],'UNKNOWN_DO_NOT_RETRY')
        second=x.run(self.signal,self.env,self.ledger,broker_get=getter,broker_post=broken)
        self.assertEqual(second['status'],'BLOCKED')
        self.assertEqual(second['reasons'],['ALREADY_ATTEMPTED_RECONCILE_FIRST'])
    def test_auto_mode_blocks_without_consolidated_risk_snapshot(self):
        self.env.update(PAPER_SIGNAL_AUTO_ENABLED='true', PAPER_EXECUTION_ENABLED='true',
                        PAPER_SIGNAL_ACCOUNT_ACK='I_AUTHORIZE_ALPACA_PAPER_ONLY',
                        PAPER_DAILY_RISK_CONFIRMED='true')
        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status':'ACTIVE','currency':'USD','trading_blocked':False,
                        'cash':'2000','equity':'2000'}
            return []
        def forbidden(*args): raise AssertionError('Order should not be posted')
        result=x.run(self.signal,self.env,self.ledger,broker_get=getter,broker_post=forbidden)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertIn('V4_PORTFOLIO_SNAPSHOT_REQUIRED',result['reasons'])

    def _auto_env_with_snapshot(self):
        snapshot=Path(self.tmp.name)/'risk.json'
        snapshot.write_text(json.dumps({'at_utc':datetime.now(timezone.utc).isoformat(),
            'alpaca_positions_count':0,'alpaca_open_orders_count':0,'complete':True,
            'daily_pnl_verified':True,'weekly_pnl_verified':True,'broker_reconciled':True,
            'positions':[],'daily_pnl_brl':'0','weekly_pnl_brl':'0',
            'available_cash_brl':'10000','has_pending_orders':False}))
        self.env.update(
            PAPER_SIGNAL_AUTO_ENABLED='true',
            PAPER_EXECUTION_ENABLED='true',
            PAPER_SIGNAL_ACCOUNT_ACK='I_AUTHORIZE_ALPACA_PAPER_ONLY',
            PAPER_DAILY_RISK_CONFIRMED='true',
            V4_RISK_SNAPSHOT_FILE=str(snapshot),
        )
        return snapshot

    def test_auto_submit_success_orders_sent_one(self):
        self._auto_env_with_snapshot()
        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status':'ACTIVE','currency':'USD','trading_blocked':False,
                        'cash':'5000','equity':'5000'}
            return []
        def poster(body, env, opener=None):
            return {'id':'mock-order-id','status':'accepted'}
        result=x.run(self.signal,self.env,self.ledger,broker_get=getter,broker_post=poster)
        self.assertEqual(result['status'],'PAPER_SUBMITTED')
        self.assertEqual(result['orders_sent'],1)
        self.assertEqual(result['broker_id'],'mock-order-id')
        lines=[json.loads(ln) for ln in Path(self.ledger).read_text().splitlines() if ln.strip()]
        self.assertTrue(any(row.get('state')=='SUBMITTED' for row in lines))
    def test_short_blocked(self):
        self.signal['side']='sell'
        self.signal['provider_signature']=sign(self.signal,self.env['SIGNAL_COPY_SECRET'])
        self.assertEqual(x.run(self.signal,self.env,self.ledger)['status'],'BLOCKED')

    @patch('src.signal_paper_runner.validate', return_value=[])
    @patch('src.risk_control_flags.demo_send_allowed', return_value=(True, None))
    def test_n30_us_equity_demo_on_paper_submitted(self, _mock_demo, _mock_validate):
        """N30.1 scenario 1: signed US_EQUITY signal submits on Alpaca paper."""
        self._auto_env_with_snapshot()
        self.signal['market'] = 'US_EQUITY'
        self.signal['provider_signature'] = sign(self.signal, self.env['SIGNAL_COPY_SECRET'])
        post_hosts = []

        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status': 'ACTIVE', 'currency': 'USD', 'trading_blocked': False,
                        'cash': '5000', 'equity': '5000'}
            return []

        def poster(body, post_env, opener=None):
            post_hosts.append(post_env.get('ALPACA_BASE_URL', '').rstrip('/'))
            return {'id': 'n30-us-order', 'status': 'accepted'}

        result = x.run(self.signal, self.env, self.ledger, broker_get=getter, broker_post=poster)
        self.assertEqual(result['status'], 'PAPER_SUBMITTED')
        self.assertEqual(result['orders_sent'], 1)
        self.assertEqual(post_hosts, [ALPACA_PAPER_HOST])

    @patch('src.signal_paper_runner.validate', return_value=[])
    @patch('src.risk_control_flags.demo_send_allowed', return_value=(True, None))
    def test_n30_crypto_risk_candidate_uses_signal_market(self, _mock_demo, _mock_validate):
        """N30.1 scenario 2: portfolio candidate market follows CRYPTO on the signal."""
        self._auto_env_with_snapshot()
        self.env['DEMO_ACCOUNT_PATH_CRYPTO'] = G_MKT_ADAPTER_PATH_ALPACA_PAPER
        crypto = dict(self.signal, market='CRYPTO', symbol='BTCUSD',
                      signal_id='N30_CRYPTO_RISK_MKT')
        crypto['provider_signature'] = sign(crypto, self.env['SIGNAL_COPY_SECRET'])
        seen = {}

        def capture_eval(candidate, snapshot):
            seen['market'] = candidate.get('market')
            return {'allowed': True, 'reasons': []}

        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status': 'ACTIVE', 'currency': 'USD', 'trading_blocked': False,
                        'cash': '5000', 'equity': '5000'}
            return []

        def poster(body, post_env, opener=None):
            return {'id': 'n30-crypto-order', 'status': 'accepted'}

        with patch.object(x, 'evaluate_portfolio_risk', side_effect=capture_eval):
            result = x.run(crypto, self.env, self.ledger, broker_get=getter, broker_post=poster)
        self.assertEqual(seen.get('market'), 'CRYPTO')
        self.assertEqual(result['status'], 'PAPER_SUBMITTED')
        self.assertEqual(result['orders_sent'], 1)

    @patch('src.signal_paper_runner.validate', return_value=[])
    def test_n30_crypto_without_named_path_blocked_no_post(self, _mock_validate):
        """N30.1 scenario 3: CRYPTO without demo path — no broker POST."""
        self._auto_env_with_snapshot()
        crypto = dict(self.signal, market='CRYPTO', symbol='BTCUSD',
                      signal_id='N30_CRYPTO_NOPATH')
        crypto['provider_signature'] = sign(crypto, self.env['SIGNAL_COPY_SECRET'])

        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status': 'ACTIVE', 'currency': 'USD', 'trading_blocked': False,
                        'cash': '5000', 'equity': '5000'}
            return []

        def forbidden_post(*_a, **_k):
            raise AssertionError('Alpaca POST must not run without named CRYPTO demo path')

        result = x.run(crypto, self.env, self.ledger, broker_get=getter, broker_post=forbidden_post)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result.get('orders_sent'), 0)
        reasons = result.get('reasons') or []
        reject = result.get('reject_code')
        self.assertTrue(reject == 'NO_DEMO_ACCOUNT_PATH' or 'NO_DEMO_ACCOUNT_PATH' in reasons)

    @patch('src.signal_paper_runner.validate', return_value=[])
    def test_n30_stale_v4_portfolio_snapshot_still_blocked(self, _mock_validate):
        """N30.1 scenario 7: snapshot older than 120s → V4_PORTFOLIO_SNAPSHOT_STALE."""
        self._auto_env_with_snapshot()
        snap_path = Path(self.env['V4_RISK_SNAPSHOT_FILE'])
        snap = json.loads(snap_path.read_text())
        stale_at = (datetime.now(timezone.utc) - timedelta(seconds=181)).isoformat()
        snap['at_utc'] = stale_at
        snap_path.write_text(json.dumps(snap))
        self.signal['market'] = 'US_EQUITY'
        self.signal['provider_signature'] = sign(self.signal, self.env['SIGNAL_COPY_SECRET'])

        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status': 'ACTIVE', 'currency': 'USD', 'trading_blocked': False,
                        'cash': '5000', 'equity': '5000'}
            return []

        def forbidden_post(*_a, **_k):
            raise AssertionError('Order must not post when V4 snapshot is stale')

        result = x.run(self.signal, self.env, self.ledger, broker_get=getter, broker_post=forbidden_post)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIn('V4_PORTFOLIO_SNAPSHOT_STALE', result.get('reasons') or [])


if __name__=='__main__':unittest.main()
