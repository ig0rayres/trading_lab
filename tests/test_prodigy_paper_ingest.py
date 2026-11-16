import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import prodigy_paper_ingest as ingest_mod
import prodigy_rank
from prodigy_rank import MIN_TRADES, WINDOW_DAYS, calculate
from strategy_catalog import DEFAULT_PHASE_BY_KEY

FIXED_NOW = datetime(2026, 6, 2, 15, 0, tzinfo=timezone.utc)
SECRET = 'x' * 32


def _rank_row(provider_id='1042'):
    return {'provider_id': provider_id, 'status': 'PRODIGY_CANDIDATE_RESEARCH', 'prodigy_score': 12.5}


def _ticket(**overrides):
    base = {
        'symbol': 'AAPL',
        'side': 'buy',
        'entry': '100',
        'stop': '99',
        'target': '102',
        'quantity': 1,
        'signal_id': 'N30_PRODIGY_TICKET_001',
        'ttl_seconds': 30,
    }
    base.update(overrides)
    return base


def _env(**extra):
    env = {
        'LIVE_TRADING_ENABLED': 'false',
        'SIGNAL_COPY_SECRET': SECRET,
        'USD_BRL_REFERENCE': '5.0',
        'ALPACA_API_KEY': 'paper-key',
        'ALPACA_SECRET_KEY': 'paper-secret',
        'ALPACA_PAPER_TRADE': 'true',
        'ALPACA_BASE_URL': 'https://paper-api.alpaca.markets',
    }
    env.update(extra)
    return env


class ProdigyPaperIngestTest(unittest.TestCase):
    def test_maps_rank_provider_and_ticket_to_prodigy_strategy(self):
        signal, err = ingest_mod.map_rank_to_signal(_rank_row(), _ticket(), SECRET, now=FIXED_NOW)
        self.assertIsNone(err)
        assert signal is not None
        self.assertEqual(signal['provider'], '1042')
        self.assertEqual(signal['strategy_key'], 'prodigy_15d')
        self.assertIn('provider_signature', signal)

    def test_research_phase_blocks_with_strategy_phase_blocked(self):
        out = ingest_mod.ingest(_rank_row(), _ticket(), _env(), now=FIXED_NOW)
        self.assertEqual(out['status'], 'BLOCKED')
        self.assertEqual(out['reject_code'], 'STRATEGY_PHASE_BLOCKED')
        self.assertEqual(out['orders_sent'], 0)
        self.assertFalse(out['execution_authorized'])
        self.assertEqual(out['signal']['strategy_key'], 'prodigy_15d')

    @patch('prodigy_paper_ingest.validate', return_value=[])
    @patch(
        'prodigy_paper_ingest.evaluate_signed_signal',
        return_value={'decision': 'paper_allowed', 'risk_amount_cents': 500},
    )
    def test_paper_limited_may_call_process_after_gate_b(self, _mock_eval, _mock_validate):
        seen = {}

        def fake_process(signal, decision, env, **kwargs):
            seen['called'] = True
            return {'status': 'QUEUED', 'orders_sent': 0, 'mode': 'PAPER_GATEWAY_QUEUE_ONLY'}

        out = ingest_mod.ingest(
            _rank_row(),
            _ticket(),
            _env(),
            strategy_phase='paper_limited',
            dry_run=False,
            now=FIXED_NOW,
            process_fn=fake_process,
        )
        self.assertTrue(seen.get('called'))
        self.assertEqual(out['status'], 'QUEUED')
        self.assertEqual(out['orders_sent'], 0)

    def test_missing_ticket_prices_ticket_fields_required(self):
        out = ingest_mod.ingest(_rank_row(), _ticket(entry=None), _env(), now=FIXED_NOW)
        self.assertEqual(out['reject_code'], 'TICKET_FIELDS_REQUIRED')
        self.assertEqual(out['orders_sent'], 0)
        self.assertNotIn('signal', out)

    def test_never_paper_strategy_rejected(self):
        out = ingest_mod.ingest(
            _rank_row(),
            _ticket(strategy_key='orb'),
            _env(),
            now=FIXED_NOW,
        )
        self.assertEqual(out['reject_code'], 'STRATEGY_NOT_PAPER')

    def test_default_phase_prodigy_still_research(self):
        self.assertEqual(DEFAULT_PHASE_BY_KEY.get('prodigy_15d'), 'research')

    def test_prodigy_rank_formula_unchanged(self):
        self.assertEqual(MIN_TRADES, 5)
        self.assertEqual(WINDOW_DAYS, 15)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            now = datetime(2026, 10, 28, tzinfo=timezone.utc)
            trades = [{'CloseDate': (now).isoformat(), 'ProfitLoss': 50} for _ in range(6)]
            payload = {
                'strategy_id': '9',
                'dataset': 'closed_trades',
                'raw': {'ResponseStatus': {'ErrorCode': '200'}, 'Results': trades},
            }
            (base / '9_closed_trades.json').write_text(json.dumps(payload))
            result = calculate(base, now)
        self.assertEqual(result['mode'], 'PRODIGY_RANK_RESEARCH_ONLY')
        self.assertFalse(result['execution_authorized'])


class ProdigyPaperIngestCliTest(unittest.TestCase):
    def test_cli_default_dry_run_orders_sent_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            rank = Path(tmp) / 'rank.json'
            ticket = Path(tmp) / 'ticket.json'
            rank.write_text(json.dumps(_rank_row()))
            ticket.write_text(json.dumps(_ticket()))
            env = {**os.environ, **_env()}
            proc = subprocess.run(
                [sys.executable, '-m', 'prodigy_paper_ingest', '--rank-row', str(rank), '--ticket', str(ticket)],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1] / 'src'),
                env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            body = json.loads(proc.stdout)
            self.assertEqual(body.get('orders_sent'), 0)

    def test_cli_rejects_live_trading_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            rank = Path(tmp) / 'rank.json'
            ticket = Path(tmp) / 'ticket.json'
            rank.write_text(json.dumps(_rank_row()))
            ticket.write_text(json.dumps(_ticket()))
            env = {**os.environ, **_env(LIVE_TRADING_ENABLED='true')}
            proc = subprocess.run(
                [sys.executable, 'prodigy_paper_ingest.py', '--rank-row', str(rank), '--ticket', str(ticket)],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1] / 'src'),
                env=env,
            )
            self.assertEqual(proc.returncode, 2)
            body = json.loads(proc.stdout)
            self.assertEqual(body.get('reject_code'), 'LIVE_TRADING_DISABLED_REQUIRED')

    def test_run_sh_defines_prodigy_ingest_case(self):
        run_sh = (Path(__file__).resolve().parents[1] / 'scripts' / 'run.sh').read_text()
        self.assertIn('prodigy-ingest)', run_sh)
        self.assertIn('prodigy_paper_ingest.py', run_sh)


if __name__ == '__main__':
    unittest.main()