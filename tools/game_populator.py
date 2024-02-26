from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def get_game_info(game_identifier: str):
    parsed_url = urlparse(game_identifier)
    if parsed_url.netloc and parsed_url.scheme:
        url = game_identifier
    else:
        url = f'http://redump.org/disc/{game_identifier}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error in request: {e}")
        return None

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find('h1')
    if title:
        title = title.string

    system = get_value('System', soup)
    media = get_value('Media', soup)
    category = get_value('Category', soup)
    region = get_value('Region', soup, 'img', 'title')
    languages = get_value('Languages', soup, 'img', 'alt')
    version = get_value('Version', soup)
    edition = get_value('Edition', soup)

    game_data = {
        "title": title,
        "system": system,
        "media": media,
        "category": category,
        "region": region,
        "languages": languages,
        "version": version,
        "edition": edition
    }

    return game_data


def get_value(label, soup, tag='td', attribute=None):
    element = soup.find('th', string=label)
    if element:
        next_element = element.find_next(tag)
        if next_element:
            if attribute:
                return next_element[attribute]
            return next_element.text.strip()

    return None
