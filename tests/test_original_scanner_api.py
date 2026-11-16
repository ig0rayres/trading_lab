import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from original import SCRIPTS, load_original


class OriginalScannerApiTests(unittest.TestCase):
    def setUp(self):
        self.repo = os.environ.get('UPSTREAM_DIR') or str(
            Path(__file__).resolve().parents[1] / 'vendor' / 'day-trader-skill'
        )

    def test_vendor_scanner_exposes_find_setups_and_rsi(self):
        orig = load_original(self.repo)
        self.assertTrue(callable(orig.scanner.find_setups))
        self.assertTrue(callable(orig.scanner.rsi))
        tags, _nums = orig.scanner.find_setups([100.0] * 29 + [99.0, 98.0, 97.0, 120.0])
        self.assertIn('breakout_20d', tags)

    def test_load_original_fails_when_find_setups_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for _name, (relative, _req) in SCRIPTS.items():
                src = Path(self.repo) / relative
                dest = root / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
            scan = root / 'trader-scanner' / 'scan.py'
            text = scan.read_text(encoding='utf-8')
            marker = 'def find_setups(closes):'
            if marker not in text:
                self.skipTest('vendor scan layout changed')
            scan.write_text(text.replace(marker, 'def find_setups_removed(closes):', 1), encoding='utf-8')
            with self.assertRaises(RuntimeError) as ctx:
                load_original(str(root))
            self.assertIn('find_setups', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()