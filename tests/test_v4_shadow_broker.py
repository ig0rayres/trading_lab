import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from v4_shadow_broker import submit_local


def ticket(market='B3_EQUITY', quantity=1):
    return {'market': market, 'symbol': 'ITUB4' if market == 'B3_EQUITY' else 'BTCBRL',
            'side': 'buy', 'quantity': quantity, 'entry_brl': 100, 'stop_brl': 95,
            'verified': True, 'trading_mode': 'PAPER',
            'strategy_id': 'too-cheap', 'signal_id': 's1'}


def snapshot():
    return {'complete': True, 'daily_pnl_verified': True, 'weekly_pnl_verified': True,
            'broker_reconciled': True, 'positions': [], 'daily_pnl_brl': 0,
            'weekly_pnl_brl': 0, 'available_cash_brl': 10000,
            'has_pending_orders': False}


def test_local_b3_intent_never_fills_or_sends(tmp_path, monkeypatch):
    monkeypatch.setenv('LIVE_TRADING_ENABLED', 'false')
    path = tmp_path/'intents.jsonl'
    result = submit_local(ticket(), snapshot(), path)
    assert result['status'] == 'PAPER_INTENT_RECORDED_NOT_FILLED'
    assert result['orders_sent'] == 0
    event = json.loads(path.read_text())
    assert event['status'] == 'PENDING_VERIFIED_MARKET_FILL'
    assert event['source'] == 'LOCAL_SIMULATOR_NO_BROKER'


def test_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv('LIVE_TRADING_ENABLED', 'false')
    path = tmp_path/'intents.jsonl'
    assert submit_local(ticket(), snapshot(), path)['status'].startswith('PAPER_')
    assert submit_local(ticket(), snapshot(), path)['reasons'] == ['DUPLICATE_PAPER_INTENT']
    assert len(path.read_text().splitlines()) == 1


def test_crypto_fractional_quantity(tmp_path, monkeypatch):
    monkeypatch.setenv('LIVE_TRADING_ENABLED', 'false')
    assert submit_local(ticket('CRYPTO', '0.125'), snapshot(), tmp_path/'intent')['status'].startswith('PAPER_')


def test_missing_reconciliation_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setenv('LIVE_TRADING_ENABLED', 'false')
    state = snapshot(); state['broker_reconciled'] = False
    result = submit_local(ticket(), state, tmp_path/'intent')
    assert 'BROKER_NOT_RECONCILED' in result['reasons']
    assert not (tmp_path/'intent').exists()


def test_live_flag_prevents_all(tmp_path, monkeypatch):
    monkeypatch.setenv('LIVE_TRADING_ENABLED', 'true')
    assert submit_local(ticket(), snapshot(), tmp_path/'intent')['status'] == 'BLOCKED'


def test_market_not_supported(tmp_path, monkeypatch):
    monkeypatch.setenv('LIVE_TRADING_ENABLED', 'false')
    assert submit_local(ticket('US_EQUITY'), snapshot(), tmp_path/'intent')['status'] == 'BLOCKED'


def test_corrupt_ledger_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setenv('LIVE_TRADING_ENABLED', 'false')
    path = tmp_path/'intents.jsonl';path.write_text('CORRUPTED\n')
    assert submit_local(ticket(), snapshot(), path)['status'] == 'BLOCKED'


def test_cannot_bypass_risk_limit(tmp_path, monkeypatch):
    monkeypatch.setenv('LIVE_TRADING_ENABLED', 'false')
    t = ticket();t['quantity'] = 20
    assert submit_local(t, snapshot(), tmp_path/'intents.jsonl')['status'] == 'BLOCKED'


def test_local_shadow_never_inserts_paper_fills(tmp_path, monkeypatch):
    """ADR-007 / N19.3: local B3-crypto simulator stays request log only."""
    monkeypatch.setenv('LIVE_TRADING_ENABLED', 'false')
    inserted_tables: list[str] = []

    def capture_insert(_conn, table, _row):
        inserted_tables.append(table)
        return None

    with patch('ledger_store.insert_row', side_effect=capture_insert):
        for market in ('B3_EQUITY', 'CRYPTO'):
            result = submit_local(ticket(market), snapshot(), tmp_path / f'{market}.jsonl')
            assert result['orders_sent'] == 0
    assert 'paper_fills' not in inserted_tables


class ShadowBrokerN19GuardTest(unittest.TestCase):
    """unittest entry for N19.3 shadow broker ledger guard."""

    def test_local_shadow_never_inserts_paper_fills(self):
        os.environ['LIVE_TRADING_ENABLED'] = 'false'
        inserted_tables: list[str] = []

        def capture_insert(_conn, table, _row):
            inserted_tables.append(table)
            return None

        with tempfile.TemporaryDirectory() as tmp:
            with patch('ledger_store.insert_row', side_effect=capture_insert):
                for market in ('B3_EQUITY', 'CRYPTO'):
                    path = Path(tmp) / f'{market}.jsonl'
                    result = submit_local(ticket(market), snapshot(), path)
                    self.assertEqual(result['orders_sent'], 0)
            self.assertNotIn('paper_fills', inserted_tables)


if __name__ == '__main__':
    unittest.main()
