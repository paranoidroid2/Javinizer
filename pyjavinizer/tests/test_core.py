from pyjavinizer.core import extract_id
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
