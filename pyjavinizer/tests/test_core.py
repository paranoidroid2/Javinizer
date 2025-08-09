from pyjavinizer.core import extract_id


def test_extract_id_uppercase():
    assert extract_id('IPX-399.mp4') == 'IPX-399'


def test_extract_id_lowercase():
    assert extract_id('abc-123.mkv') == 'ABC-123'


def test_extract_id_missing():
    assert extract_id('noidfile.txt') is None
