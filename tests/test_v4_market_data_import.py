import hashlib
import pytest
from v4_market_data_import import load_pinned_csv

HEADER = 'at_utc,open_brl,high_brl,low_brl,close_brl\n'
ROW = '2026-10-28T14:00:00Z,10,12,9,11\n'


def load(tmp_path, data=HEADER+ROW, **overrides):
    path = tmp_path / 'candles.csv'
    path.write_text(data)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    args = dict(sha256=sha, market='B3_EQUITY', symbol='ITUB4')
    args.update(overrides)
    return load_pinned_csv(path, **args)


def test_valid_pinned_file(tmp_path):
    result = load(tmp_path)
    assert result['bar_count'] == 1
    assert result['bars'][0]['close_brl'] == '11'
    assert result['usable_for_live_trading'] is False
    assert result['independent_market_verification'] is False


def test_bad_hash(tmp_path):
    with pytest.raises(ValueError, match='SOURCE_HASH_MISMATCH'):
        load(tmp_path, sha256='0'*64)

@pytest.mark.parametrize('row', [
    '2026-10-28T14:00:00Z,10,8,9,11\n',
    '2026-10-28T14:00:00Z,10,nan,9,11\n',
    '2026-10-28T14:00:00Z,10,12,-1,11\n',
    '2026-10-28T14:00:00,10,12,9,11\n',
    '2026-10-28T14:00:00Z,10,12,9,inf\n',
])
def test_reject_bad_bars(tmp_path, row):
    with pytest.raises(ValueError):
        load(tmp_path, HEADER+row)


def test_reject_unsorted_and_duplicate(tmp_path):
    with pytest.raises(ValueError, match='OUT_OF_ORDER'):
        load(tmp_path, HEADER + ROW + ROW)


def test_reject_fx_assumption(tmp_path):
    with pytest.raises(ValueError, match='CURRENCY_CONVERSION_REQUIRED'):
        load(tmp_path, denomination='USD')


def test_reject_extra_columns(tmp_path):
    with pytest.raises(ValueError, match='INVALID_COLUMNS'):
        load(tmp_path, HEADER.replace('close_brl','close_brl,volume') + ROW.replace('11\n','11,10\n'))


def test_reject_empty(tmp_path):
    with pytest.raises(ValueError, match='EMPTY_DATA'):
        load(tmp_path, HEADER)


def test_reject_unsupported_market(tmp_path):
    with pytest.raises(ValueError, match='INVALID_MARKET_OR_SYMBOL'):
        load(tmp_path, market='B3_OPTIONS')
