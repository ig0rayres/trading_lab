"""Traceability: every catalog strategy_key has a homolog row in TEST-EVIDENCE N13 matrix."""
import unittest

from strategy_catalog import DEFAULT_PHASE_BY_KEY, KNOWN_STRATEGY_KEYS, NEVER_PAPER_KEYS

# Keep in sync with docs/TEST-EVIDENCE.md § Sprint N13 table (strategy_key column).
DOCUMENTED_KEYS = frozenset(
    {
        'news_first',
        'momentum',
        'ta_barato',
        'prodigy_15d',
        'signal_copy',
        'orb',
        'mean_reversion',
    }
)

UPSTREAM_BLOCKED = frozenset({'momentum', 'ta_barato', 'prodigy_15d'})


class StrategyHomologTraceabilityTests(unittest.TestCase):
    def test_documented_keys_match_catalog(self):
        self.assertEqual(DOCUMENTED_KEYS, KNOWN_STRATEGY_KEYS)
        for key in KNOWN_STRATEGY_KEYS:
            self.assertIn(key, DEFAULT_PHASE_BY_KEY)

    def test_never_paper_keys_are_shadow_family(self):
        for key in NEVER_PAPER_KEYS:
            self.assertEqual(DEFAULT_PHASE_BY_KEY[key], 'shadow')

    def test_signal_copy_only_default_paper_limited(self):
        paper_limited = [k for k, ph in DEFAULT_PHASE_BY_KEY.items() if ph == 'paper_limited']
        self.assertEqual(paper_limited, ['signal_copy'])

    def test_upstream_blocked_not_paper_phases(self):
        for key in UPSTREAM_BLOCKED:
            self.assertIn(DEFAULT_PHASE_BY_KEY[key], ('research',))


if __name__ == '__main__':
    unittest.main()
