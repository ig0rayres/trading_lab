import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import strategy_catalog as sc


class StrategyCatalogTest(unittest.TestCase):
    def test_default_phases_match_dbml_families(self):
        self.assertEqual(sc.DEFAULT_PHASE_BY_KEY['signal_copy'], 'paper_limited')
        self.assertEqual(sc.DEFAULT_PHASE_BY_KEY['orb'], 'shadow')
        self.assertEqual(len(sc.DEFAULT_PHASE_BY_KEY), len(sc.KNOWN_STRATEGY_KEYS))

    def test_orb_never_paper_even_if_phase_paper(self):
        code = sc.gate_b_strategy_reject(
            {'strategy_key': 'orb'},
            strategy_phase='paper_limited',
        )
        self.assertEqual(code, 'STRATEGY_NOT_PAPER')

    def test_research_blocks_paper(self):
        code = sc.gate_b_strategy_reject(
            {'strategy_key': 'signal_copy'},
            strategy_phase='research',
        )
        self.assertEqual(code, 'STRATEGY_PHASE_BLOCKED')

    def test_paper_limited_allows_signal_copy(self):
        code = sc.gate_b_strategy_reject(
            {'strategy_key': 'signal_copy'},
            strategy_phase='paper_limited',
        )
        self.assertIsNone(code)

    def test_missing_key(self):
        self.assertEqual(sc.gate_b_strategy_reject({}), 'STRATEGY_KEY_REQUIRED')

    def test_unknown_key(self):
        self.assertEqual(
            sc.gate_b_strategy_reject({'strategy_key': 'not_a_family'}),
            'STRATEGY_UNKNOWN',
        )


if __name__ == '__main__':
    unittest.main()
