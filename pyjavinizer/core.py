import re
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup

ID_PATTERN = re.compile(r'([A-Za-z]{2,5}-\d{2,5})', re.IGNORECASE)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.5'
}
COOKIES = {'over18': '18', 'lang': 'en'}


def extract_id(filename: str) -> Optional[str]:
    """Extract a JAV ID (e.g. IPX-399) from a filename."""
    match = ID_PATTERN.search(filename)
    return match.group(1).upper() if match else None


def search_javlibrary(jav_id: str) -> Optional[str]:
    """Search JavLibrary for the given ID and return the video page URL."""
    search_url = f'https://www.javlibrary.com/en/vl_searchbyid.php?keyword={jav_id}'
    response = requests.get(search_url, headers=HEADERS, cookies=COOKIES, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    link = soup.select_one('div.video a')
    if not link:
        return None
    href = link.get('href')
    if not href:
        return None
    return 'https://www.javlibrary.com' + href


def get_metadata(url: str) -> Dict[str, Optional[str]]:
    """Fetch metadata from a JavLibrary video page."""
    response = requests.get(url, headers=HEADERS, cookies=COOKIES, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    def get_data(element_id, selector=None, attribute=None):
        container = soup.find('div', id=element_id)
        if not container:
            return None
        value_td = container.find('td', class_='text')
        if not value_td:
            tds = container.find_all('td')
            if len(tds) > 1:
                value_td = tds[1]
            else:
                return None
        element = value_td.select_one(selector) if selector else value_td
        if not element:
            return None
        return element.get(attribute, '').strip() if attribute else element.text.strip()

    data: Dict[str, Optional[str]] = {}
    data['id'] = get_data('video_id')
    title_tag = soup.find('title')
    if title_tag:
        full_title = title_tag.text.split(' - ')[0].strip()
        if data['id']:
            full_title = full_title.replace(data['id'], '').strip()
        data['title'] = full_title
    else:
        data['title'] = None
    data['release_date'] = get_data('video_date')
    data['runtime'] = get_data('video_length')
    data['director'] = get_data('video_director', 'a')
    data['maker'] = get_data('video_maker', 'a')
    data['label'] = get_data('video_label', 'a')

    rating_text = get_data('video_review', 'span.score')
    data['rating'] = rating_text.replace('(', '').replace(')', '') if rating_text else None

    genres = []
    genre_container = soup.find('div', id='video_genres')
    if genre_container:
        for link in genre_container.select('td.text span.genre a'):
            genres.append(link.text.strip())
    data['genres'] = genres or None

    actresses = []
    cast_container = soup.find('div', id='video_cast')
    if cast_container:
        for star in cast_container.select('td.text span.star'):
            name_tag = star.find('a')
            if name_tag:
                actresses.append(name_tag.text.strip())
    data['actresses'] = actresses or None

    cover_img = soup.find('img', id='video_jacket_img')
    if cover_img:
        cover_url = cover_img.get('src')
        if cover_url and cover_url.startswith('//'):
            cover_url = 'https:' + cover_url
        data['cover_url'] = cover_url
    else:
        data['cover_url'] = None

    return data


def create_nfo(metadata: Dict[str, Optional[str]], nfo_path: Path) -> None:
    """Create a minimal NFO (XML) file with metadata."""
    movie = ET.Element('movie')
    ET.SubElement(movie, 'title').text = metadata.get('title') or ''
    ET.SubElement(movie, 'id').text = metadata.get('id') or ''
    if metadata.get('maker'):
        ET.SubElement(movie, 'studio').text = metadata['maker']
    if metadata.get('release_date'):
        ET.SubElement(movie, 'premiered').text = metadata['release_date']
    if metadata.get('runtime'):
        ET.SubElement(movie, 'runtime').text = metadata['runtime']
    tree = ET.ElementTree(movie)
    tree.write(nfo_path, encoding='utf-8', xml_declaration=True)


def sort_file(source: Path, dest_root: Path, metadata: Dict[str, Optional[str]]) -> Path:
    """Move the file to a sorted folder based on metadata and write an NFO file."""
    studio = metadata.get('maker') or 'Unknown'
    title = metadata.get('title') or 'Unknown'
    dest_dir_name = f"{metadata.get('id', source.stem)} [{studio}] - {title}"
    dest_dir = dest_root / dest_dir_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_file = dest_dir / source.name
    shutil.move(str(source), dest_file)

    nfo_path = dest_dir / f"{metadata.get('id', source.stem)}.nfo"
    create_nfo(metadata, nfo_path)
    return dest_file
