import json
import logging

from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

def parse_html(content: str) -> Optional[BeautifulSoup]:

    if not content:
        return None

    try:
        soup = BeautifulSoup(content, 'html.parser')
        return soup
    except Exception as e:
        logger.warning(f"Error parsing HTML: {e}")
        return None

def parse_json(content: str) -> Optional[Dict[str, Any]]:

    if not content:
        return None

    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError as e:
        logger.warning(f"Error parsing JSON: {e}")
        return None

def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:

    meta_data = {}

    if not soup:
        return meta_data

    try:

        for meta in soup.find_all('meta'):

            key = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            value = meta.get('content')

            if key and value:
                meta_data[key] = value

        title = soup.find('title')
        if title and title.string:
            meta_data['title'] = title.string.strip()

        return meta_data

    except Exception as e:
        logger.warning(f"Error extracting meta tags: {e}")
        return meta_data

def get_content_type_category(content_type: str) -> str:

    if not content_type:
        return 'other'

    content_type_lower = content_type.lower()

    if 'text/html' in content_type_lower:
        return 'html'
    elif 'application/json' in content_type_lower or 'application/ld+json' in content_type_lower:
        return 'json'
    elif 'application/xml' in content_type_lower or 'text/xml' in content_type_lower:
        return 'xml'
    elif content_type_lower.startswith('image/'):
        return 'image'
    elif content_type_lower.startswith('video/'):
        return 'video'
    elif content_type_lower.startswith('audio/'):
        return 'audio'
    else:
        return 'other'

def extract_links_from_html(soup: BeautifulSoup, base_url: str = None) -> List[Dict[str, str]]:

    from urllib.parse import urljoin

    links = []

    if not soup:
        return links

    try:
        for anchor in soup.find_all('a', href=True):
            href = anchor['href'].strip()

            if not href or href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue

            if base_url and not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)

            link_info = {
                'url': href,
                'text': anchor.get_text(strip=True),
                'title': anchor.get('title', '')
            }

            links.append(link_info)

        return links

    except Exception as e:
        logger.warning(f"Error extracting links: {e}")
        return links