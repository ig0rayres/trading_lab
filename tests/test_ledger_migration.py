import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIG = ROOT / 'migrations'

LEDGER_TABLES = {
    'strategy_states',
    'signal_events',
    'risk_decisions',
    'positions',
    'paper_orders',
    'paper_fills',
    'ledger_entries',
    'control_flags',
}


class LedgerMigrationFilesTest(unittest.TestCase):
    def test_up_defines_all_ledger_tables(self):
        up = (MIG / '001_ledger_up.sql').read_text(encoding='utf-8').lower()
        for name in LEDGER_TABLES:
            self.assertIn('create table %s' % name, up, name)

    def test_down_drops_all_ledger_tables(self):
        down = (MIG / '001_ledger_down.sql').read_text(encoding='utf-8').lower()
        for name in LEDGER_TABLES:
            self.assertIn('drop table if exists %s' % name, down, name)


@unittest.skipUnless(os.environ.get('LEDGER_DATABASE_URL'), 'LEDGER_DATABASE_URL not set')
class LedgerMigrationIntegrationTest(unittest.TestCase):
    def test_apply_rollback_roundtrip(self):
        import sys
        sys.path.insert(0, str(ROOT / 'src'))
        import ledger_migrate as lm

        lm.rollback()
        self.assertFalse(lm.status()['applied'])
        lm.apply()
        self.assertTrue(lm.status()['applied'])
        lm.rollback()
        self.assertFalse(lm.status()['applied'])
        lm.apply()
        self.assertTrue(lm.status()['applied'])


if __name__ == '__main__':
    unittest.main()
