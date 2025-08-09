from pyjavinizer.core import extract_id, search_javlibrary
from unittest.mock import patch
import requests
from pyjavinizer.cli import gather_files


def test_extract_id_uppercase():
    assert extract_id('IPX-399.mp4') == 'IPX-399'


def test_extract_id_lowercase():
    assert extract_id('abc-123.mkv') == 'ABC-123'


def test_extract_id_missing():
    assert extract_id('noidfile.txt') is None


def test_gather_files_filters(tmp_path):
    media = tmp_path / 'movie.mp4'
    media.touch()
    (tmp_path / 'ignore.txt').touch()

    files = list(gather_files(tmp_path, recursive=False))
    assert files == [media]


def test_gather_files_recursive(tmp_path):
    sub = tmp_path / 'sub'
    sub.mkdir()
    nested = sub / 'clip.mkv'
    nested.touch()

    files = list(gather_files(tmp_path, recursive=True))
    assert nested in files


def test_search_redirect():
    mock_resp = requests.Response()
    mock_resp.status_code = 200
    mock_resp.url = 'https://www.javlibrary.com/en/?v=abcd1234'
    mock_resp._content = b''

    with patch('pyjavinizer.core.requests.get', return_value=mock_resp):
        assert search_javlibrary('XMOM-065') == mock_resp.url
