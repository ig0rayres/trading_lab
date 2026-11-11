import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import risk_control_flags as rcf


class RiskControlFlagsTest(unittest.TestCase):
    def test_tight_defaults_when_no_dsn(self):
        with patch.dict(os.environ, {}, clear=True):
            flags = rcf.fetch_control_flags()
        self.assertEqual(flags['capital_cents'], 500_000)
        self.assertEqual(flags['max_risk_per_trade_cents'], 5_000)
        self.assertFalse(flags['demo_operation_on'])

    def test_db_error_falls_back_to_tight_defaults(self):
        def boom():
            raise RuntimeError('db down')

        with patch.dict(os.environ, {'LEDGER_DATABASE_URL': 'postgres://x'}, clear=False):
            flags = rcf.fetch_control_flags(conn_factory=boom)
        self.assertEqual(flags['capital_cents'], 500_000)
        self.assertEqual(flags['max_risk_per_trade_cents'], 5_000)

    def test_merge_row_overrides_capital(self):
        row = (
            False,
            False,
            400_000,
            4_000,
            2,
            15_000,
            15_000,
            40_000,
            1_500,
        )
        flags = rcf.merge_row(row)
        self.assertEqual(flags['capital_cents'], 400_000)
        self.assertEqual(flags['max_open_positions'], 2)
        self.assertEqual(rcf.brl_from_cents(400_000), Decimal('4000'))

    def test_demo_send_blocked_by_default(self):
        ok, reason = rcf.demo_send_allowed()
        self.assertFalse(ok)
        self.assertEqual(reason, 'DEMO_OPERATION_OFF')


if __name__ == '__main__':
    unittest.main()
