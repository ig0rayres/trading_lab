import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import gate_b_session as gs


class GateBSessionTest(unittest.TestCase):
    def test_ny_holiday_closed(self):
        thanksgiving = datetime(2026, 11, 26, 15, 0, tzinfo=ZoneInfo('America/New_York'))
        self.assertFalse(gs.within_regular_session(thanksgiving))

    def test_ny_weekday_inside_session(self):
        from original import load_original

        risk = load_original().risk
        inside = risk.parse_now('2026-10-28 10:15')
        self.assertTrue(gs.within_regular_session(inside))

    def test_b3_weekend_closed(self):
        saturday_sp = datetime(2026, 11, 7, 12, 0, tzinfo=ZoneInfo('America/Sao_Paulo'))
        self.assertFalse(gs.within_b3_session(saturday_sp))

    def test_b3_weekday_inside_session(self):
        wednesday = datetime(2026, 11, 5, 14, 0, tzinfo=ZoneInfo('America/Sao_Paulo'))
        self.assertTrue(gs.within_b3_session(wednesday))

    def test_b3_weekday_before_open(self):
        early = datetime(2026, 11, 5, 9, 30, tzinfo=ZoneInfo('America/Sao_Paulo'))
        self.assertFalse(gs.within_b3_session(early))

    def test_signal_market_routing(self):
        sig = {'asset_class': 'b3_equity', 'symbol': 'ITUB4'}
        self.assertEqual(gs.market_from_signal(sig), 'B3_EQUITY')
        self.assertFalse(
            gs.within_signal_session(
                sig,
                datetime(2026, 11, 7, 12, 0, tzinfo=timezone.utc),
            )
        )


if __name__ == '__main__':
    unittest.main()
