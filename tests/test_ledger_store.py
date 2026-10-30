import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import ledger_store as store


class LedgerStoreTest(unittest.TestCase):
    def test_soft_delete_forbidden_on_fills(self):
        with self.assertRaisesRegex(ValueError, 'SOFT_DELETE_FORBIDDEN'):
            store.assert_no_soft_delete('paper_fills', {'deleted_at': '2026-01-01'})

    def test_unknown_table(self):
        with self.assertRaisesRegex(ValueError, 'UNKNOWN_TABLE'):
            store.insert_row(None, 'not_a_table', {'id': 1})


if __name__ == '__main__':
    unittest.main()
