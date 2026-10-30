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
    def _count_strategy_keys(self):
        import sys

        sys.path.insert(0, str(ROOT / 'src'))
        import ledger_migrate as lm
        from strategy_catalog import KNOWN_STRATEGY_KEYS

        with lm._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT strategy_key FROM strategy_states WHERE deleted_at IS NULL'
                )
                found = {row[0] for row in cur.fetchall()}
        return found, KNOWN_STRATEGY_KEYS

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

    def test_apply_seeds_seven_strategy_states(self):
        import sys

        sys.path.insert(0, str(ROOT / 'src'))
        import ledger_migrate as lm

        lm.rollback()
        result = lm.apply()
        self.assertEqual(result.get('strategy_seed'), 'ok')
        found, expected = self._count_strategy_keys()
        self.assertEqual(found, expected)

    def test_already_applied_re_seeds_without_clobber(self):
        import sys

        sys.path.insert(0, str(ROOT / 'src'))
        import ledger_migrate as lm

        lm.apply()
        with lm._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE strategy_states SET phase = 'paper_validated' "
                    "WHERE strategy_key = 'orb' AND deleted_at IS NULL"
                )
            conn.commit()
        result = lm.apply()
        self.assertEqual(result['status'], 'already_applied')
        with lm._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT phase FROM strategy_states WHERE strategy_key = 'orb'"
                )
                phase = cur.fetchone()[0]
        self.assertEqual(phase, 'paper_validated')


if __name__ == '__main__':
    unittest.main()
