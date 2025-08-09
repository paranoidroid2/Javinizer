"""Command-line interface for the simplified PyJavinizer tool."""

import argparse
from pathlib import Path

from .core import extract_id, search_javlibrary, get_metadata, sort_file


def gather_files(path: Path, recursive: bool):
    """Yield media files from *path*, recursing into directories when requested."""

    if path.is_file():
        yield path
    else:
        iterator = path.rglob('*') if recursive else path.iterdir()
        for p in iterator:
            if p.is_file() and p.suffix.lower() in {'.mp4', '.mkv', '.avi', '.wmv', '.mov'}:
                yield p


def main() -> None:
    """Entry point for the CLI tool."""

    parser = argparse.ArgumentParser(description='Simplified Javinizer (Python)')
    parser.add_argument('path', help='Path to file or directory to sort')
    parser.add_argument('destination', help='Destination directory')
    parser.add_argument('-r', '--recurse', action='store_true', help='Recurse into directories')
    args = parser.parse_args()

    src_path = Path(args.path)
    dest_root = Path(args.destination)
    dest_root.mkdir(parents=True, exist_ok=True)

    for file_path in gather_files(src_path, args.recurse):
        jav_id = extract_id(file_path.name)
        if not jav_id:
            print(f'Skipping {file_path}: unable to parse ID')
            continue
        url = search_javlibrary(jav_id)
        if not url:
            print(f'Metadata for {jav_id} not found')
            continue
        metadata = get_metadata(url)
        sort_file(file_path, dest_root, metadata)
        print(f'Sorted {file_path} -> {metadata.get("id", jav_id)}')


if __name__ == '__main__':
    main()
