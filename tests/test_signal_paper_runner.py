import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from decimal import Decimal

from src import signal_paper_runner as x
from src.demo_broker_adapters import G_MKT_ADAPTER_PATH_ALPACA_PAPER
from src.risk_control_flags import TIGHT_DEFAULTS
from src.signal_copy import sign

ALPACA_PAPER_HOST = 'https://paper-api.alpaca.markets'


def _control_flags(**overrides):
    flags = dict(TIGHT_DEFAULTS)
    flags.update(overrides)
    return flags

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

    def _broker_getter(self):
        def getter(endpoint, env):
            if endpoint.endswith('account'):
                return {'status': 'ACTIVE', 'currency': 'USD', 'trading_blocked': False,
                        'cash': '5000', 'equity': '5000'}
            return []
        return getter

    def _tracking_poster(self):
        calls = []

        def poster(body, post_env, opener=None):
            calls.append(True)
            return {'id': 'must-not-submit', 'status': 'accepted'}

        return calls, poster

    @patch('src.signal_paper_runner.validate', return_value=[])
    @patch('src.risk_control_flags.demo_send_allowed', return_value=(True, None))
    @patch('src.signal_paper_runner.fetch_control_flags', create=True)
    def test_n32_tight_defaults_qty1_aapl_paper_submitted(self, mock_flags, _demo, _validate):
        """N32.2 scenario 1: TIGHT_DEFAULTS + qty=1 AAPL stays on PAPER_SUBMITTED path."""
        mock_flags.return_value = _control_flags()
        self._auto_env_with_snapshot()
        self.assertEqual(self.env.get('LIVE_TRADING_ENABLED'), 'false')
        getter = self._broker_getter()
        post_called, poster = self._tracking_poster()
        result = x.run(self.signal, self.env, self.ledger, broker_get=getter, broker_post=poster)
        self.assertEqual(result['status'], 'PAPER_SUBMITTED')
        self.assertEqual(result['orders_sent'], 1)
        self.assertTrue(post_called)

    @patch('src.signal_paper_runner.validate', return_value=[])
    @patch('src.risk_control_flags.demo_send_allowed', return_value=(True, None))
    @patch('src.signal_paper_runner.fetch_control_flags', create=True)
    def test_n32_lowered_capital_cents_blocks_capital_limit(self, mock_flags, _demo, _validate):
        """N32.2 scenario 2: lowered capital_cents → BLOCKED, CAPITAL_LIMIT, no POST."""
        mock_flags.return_value = _control_flags(capital_cents=5_000)
        self._auto_env_with_snapshot()
        getter = self._broker_getter()
        post_calls, poster = self._tracking_poster()
        result = x.run(self.signal, self.env, self.ledger, broker_get=getter, broker_post=poster)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result.get('orders_sent'), 0)
        self.assertFalse(post_calls, 'poster must not run when capital anchor blocks')
        reasons = result.get('reasons') or []
        self.assertTrue('CAPITAL_LIMIT' in reasons or 'TOTAL_CAP_EXCEEDED' in reasons)

    @patch('src.signal_paper_runner.validate', return_value=[])
    @patch('src.risk_control_flags.demo_send_allowed', return_value=(True, None))
    @patch('src.signal_paper_runner.fetch_control_flags', create=True)
    def test_n32_lowered_max_risk_per_trade_blocks_trade_risk_limit(
        self, mock_flags, _demo, _validate,
    ):
        """N32.2 scenario 3: lowered max_risk_per_trade_cents → TRADE_RISK_LIMIT."""
        mock_flags.return_value = _control_flags(max_risk_per_trade_cents=50)
        self._auto_env_with_snapshot()
        getter = self._broker_getter()
        post_calls, poster = self._tracking_poster()
        result = x.run(self.signal, self.env, self.ledger, broker_get=getter, broker_post=poster)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result.get('orders_sent'), 0)
        self.assertFalse(post_calls, 'poster must not run when trade risk anchor blocks')
        self.assertIn('TRADE_RISK_LIMIT', result.get('reasons') or [])

    @patch('src.signal_paper_runner.fetch_control_flags', create=True)
    @patch.object(x, 'evaluate_portfolio_risk', return_value={'reasons': []})
    def test_n32_risk_check_tight_cap_not_parallel_10k_usd(self, _mock_eval, mock_flags):
        """N32.2 scenario 4: parallel cap follows TIGHT (R$5k), not hardcoded 10k USD."""
        mock_flags.return_value = _control_flags()
        self._auto_env_with_snapshot()
        fx = Decimal(self.env['USD_BRL_REFERENCE'])
        account = {'status': 'ACTIVE', 'currency': 'USD', 'trading_blocked': False,
                   'cash': '5000', 'equity': '5000'}
        ticket = dict(self.signal, entry=1500, stop=1499, target=1510, quantity=1)
        reasons = x.risk_check(ticket, account, [], [], fx, self.env)
        self.assertIn('CAPITAL_LIMIT', reasons)

    @patch('src.signal_paper_runner.validate', return_value=[])
    def test_n32_b3_equity_auto_blocked_no_alpaca_post(self, _mock_validate):
        """N32.2 scenario 5a: B3_EQUITY stays NO_DEMO_ACCOUNT_PATH, orders_sent=0."""
        self._auto_env_with_snapshot()
        b3 = dict(self.signal, market='B3_EQUITY', symbol='ITUB4', signal_id='N32_B3_RUNNER')
        b3['provider_signature'] = sign(b3, self.env['SIGNAL_COPY_SECRET'])
        getter = self._broker_getter()
        post_calls, poster = self._tracking_poster()
        result = x.run(b3, self.env, self.ledger, broker_get=getter, broker_post=poster)
        self.assertFalse(post_calls)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result.get('orders_sent'), 0)
        reasons = result.get('reasons') or []
        reject = result.get('reject_code')
        self.assertTrue(
            reject == 'NO_DEMO_ACCOUNT_PATH' or 'NO_DEMO_ACCOUNT_PATH' in reasons,
        )

    @patch('src.signal_paper_runner.validate', return_value=[])
    def test_n32_forex_auto_blocked_no_alpaca_post(self, _mock_validate):
        """N32.2 scenario 5b: FOREX stays NO_DEMO_ACCOUNT_PATH, orders_sent=0."""
        self._auto_env_with_snapshot()
        fx_sig = dict(self.signal, market='FOREX', symbol='EURUSD', signal_id='N32_FOREX_RUNNER')
        fx_sig['provider_signature'] = sign(fx_sig, self.env['SIGNAL_COPY_SECRET'])
        getter = self._broker_getter()
        post_calls, poster = self._tracking_poster()
        result = x.run(fx_sig, self.env, self.ledger, broker_get=getter, broker_post=poster)
        self.assertFalse(post_calls)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result.get('orders_sent'), 0)
        reasons = result.get('reasons') or []
        reject = result.get('reject_code')
        self.assertTrue(
            reject == 'NO_DEMO_ACCOUNT_PATH' or 'NO_DEMO_ACCOUNT_PATH' in reasons,
        )


if __name__=='__main__':unittest.main()
