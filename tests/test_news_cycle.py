import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from news_cycle import window, execute

class CycleTests(unittest.TestCase):
    def test_window(self):
        self.assertEqual(window(3, datetime(2026,10,28,tzinfo=timezone.utc)),('2026-10-25','2026-10-29'))
    def test_bad_days(self):
        with self.assertRaises(ValueError): window(30)
    def test_no_broker_order(self):
        with self.assertRaises(ValueError):
            execute('bogus','BTCUSD','2026-10-01','2026-10-02',3,'/tmp')
