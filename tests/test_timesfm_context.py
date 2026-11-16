import os
import unittest
from unittest.mock import patch

from timesfm_context import build_timesfm_block, run_timesfm_forecast


class TimesFmContextTests(unittest.TestCase):
    def test_default_env_is_unavailable_without_fake_numbers(self):
        with patch.dict(os.environ, {}, clear=True):
            block = build_timesfm_block(day='2026-11-16', context_values=[1.0, 2.0, 3.0, 4.0])
        self.assertEqual(block['timesfm_status'], 'UNAVAILABLE')
        self.assertEqual(block['tips'], [])
        self.assertNotIn('forecast', block)
        self.assertNotIn('forecast_values', block)

    def test_enabled_without_checkpoint_stays_unavailable(self):
        with patch.dict(os.environ, {'TIMESFM_ENABLED': '1'}, clear=True):
            block = build_timesfm_block(day='2026-11-16', context_values=[1.0, 2.0, 3.0, 4.0])
        self.assertEqual(block['timesfm_status'], 'UNAVAILABLE')
        self.assertEqual(block['tips'], [])

    def test_runner_success_yields_research_tip_only(self):
        def _fake_runner(_series, *, horizon, checkpoint):
            return {'model_id': checkpoint, 'horizon': horizon, 'forecast_shape': (8,)}

        with patch.dict(
            os.environ,
            {'TIMESFM_ENABLED': '1', 'TIMESFM_CHECKPOINT': 'google/timesfm-test-stub'},
            clear=True,
        ):
            block = build_timesfm_block(
                day='2026-11-16',
                context_values=[1.0, 2.0, 3.0, 4.0],
                forecast_runner=_fake_runner,
            )
        self.assertEqual(block['timesfm_status'], 'OK')
        self.assertEqual(len(block['tips']), 1)
        tip = block['tips'][0]
        self.assertEqual(tip['label'], 'research_tip')
        self.assertFalse(tip['paper_allowed'])
        self.assertFalse(tip['execution_authorized'])
        self.assertEqual(tip['orders_sent'], 0)
        self.assertNotIn('forecast', block['metadata'])


if __name__ == '__main__':
    unittest.main()