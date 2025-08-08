import sys
import requests
from bs4 import BeautifulSoup
import json

def get_data(soup, element_id, selector, attribute=None):
    """Helper function to extract data from soup object."""
    try:
        container = soup.find('div', id=element_id)
        if not container:
            return None

        # The HTML structure seems to be <div..><table..><tr..><td..>Header</td><td..>Value</td>
        value_td = container.find('td', class_='text')
        if not value_td:
             # some elements are in the second td without a class
             all_tds = container.find_all('td')
             if len(all_tds) > 1:
                 value_td = all_tds[1]
             else:
                 return None

        if selector:
            element = value_td.select_one(selector)
        else:
            element = value_td

        if not element:
            return None

        if attribute:
            return element.get(attribute, '').strip()
        else:
            return element.text.strip()
    except Exception:
        return None

def get_genres(soup):
    """Helper function to get genres."""
    genres = []
    container = soup.find('div', id='video_genres')
    if container:
        links = container.select('td.text span.genre a')
        for link in links:
            genres.append(link.text.strip())
    return genres if genres else None

def get_actresses(soup):
    """Helper function to get actresses."""
    actresses = []
    container = soup.find('div', id='video_cast')
    if container:
        stars = container.select('td.text span.star')
        for star in stars:
            name_tag = star.find('a')
            if name_tag:
                actresses.append(name_tag.text.strip())
    return actresses if actresses else None


def get_javlibrary_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    try:
        # Javlibrary uses cookies to determine language, let's try to force english
        cookies = {'over18': '18', 'lang': 'en'}
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"Request failed: {e}"}))
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    data = {}

    # Using helper functions to populate data
    data['id'] = get_data(soup, 'video_id', None)

    try:
        full_title = soup.find('title').text
        # "ID Full Title - JAVLibrary"
        data['title'] = full_title.split(' - ')[0].strip()
        if data['id']:
             data['title'] = data['title'].replace(data['id'], '').strip()
    except:
        data['title'] = None

    data['release_date'] = get_data(soup, 'video_date', None)
    data['runtime'] = get_data(soup, 'video_length', None)
    data['director'] = get_data(soup, 'video_director', 'a')
    data['maker'] = get_data(soup, 'video_maker', 'a')
    data['label'] = get_data(soup, 'video_label', 'a')

    try:
        rating_text = get_data(soup, 'video_review', 'span.score')
        if rating_text:
            data['rating'] = rating_text.replace('(', '').replace(')', '')
        else:
            data['rating'] = None
    except:
        data['rating'] = None

    data['genres'] = get_genres(soup)
    data['actresses'] = get_actresses(soup)

    try:
        cover_img = soup.find('img', id='video_jacket_img')
        if cover_img:
            cover_url = cover_img['src']
            if cover_url.startswith('//'):
                cover_url = 'https:' + cover_url
            data['cover_url'] = cover_url
        else:
            data['cover_url'] = None
    except:
        data['cover_url'] = None

    print(json.dumps(data, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        get_javlibrary_data(sys.argv[1])
    else:
        print(json.dumps({"error": "No URL provided"}))
        sys.exit(1)
