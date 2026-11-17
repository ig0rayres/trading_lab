import unittest
from unittest.mock import MagicMock

from operational_defaults import ensure_operational_defaults


class _FakeCursor:
    def __init__(self, conn):
        self._conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self._conn.last_sql = sql
        self._conn.last_params = params
        low = sql.lower()
        if 'from control_flags' in low and 'limit 1' in low:
            self._conn.fetchone_result = self._conn.control_row
            return
        if 'from trigger_changes' in low:
            key = (params[0], str(params[1]), params[2])
            self._conn.fetchone_result = (1,) if key in self._conn.touched else None
            return
        if 'from market_controls' in low:
            market = params[0]
            self._conn.fetchone_result = self._conn.markets.get(market)
            return
        if sql.strip().lower().startswith('insert into control_flags'):
            self._conn.inserted = True
            return
        if 'update control_flags' in low:
            self._conn.updated_flags += 1
            return
        if 'update market_controls' in low:
            self._conn.updated_markets += 1

    def fetchone(self):
        return getattr(self._conn, 'fetchone_result', None)


class _FakeConn:
    def __init__(self):
        self.control_row = None
        self.markets = {
            'B3_EQUITY': ('m1', False),
            'CRYPTO': ('m2', False),
            'FOREX': ('m3', False),
        }
        self.touched = set()
        self.inserted = False
        self.updated_flags = 0
        self.updated_markets = 0

    def cursor(self):
        return _FakeCursor(self)


class OperationalDefaultsTests(unittest.TestCase):
    def test_inserts_when_no_control_flags(self):
        conn = _FakeConn()
        stats = ensure_operational_defaults(conn)
        self.assertTrue(conn.inserted)
        self.assertEqual(stats['inserted_flags'], 1)

    def test_flips_demo_when_never_touched(self):
        conn = _FakeConn()
        conn.control_row = ('id1', False, False)
        stats = ensure_operational_defaults(conn)
        self.assertEqual(stats['control_flags'], 1)
        self.assertEqual(stats['market_controls'], 3)

    def test_respects_operator_demo_off(self):
        conn = _FakeConn()
        conn.control_row = ('id1', False, False)
        conn.touched.add(('control_flags', 'id1', 'demo_operation_on'))
        stats = ensure_operational_defaults(conn)
        self.assertEqual(stats['control_flags'], 0)


if __name__ == '__main__':
    unittest.main()