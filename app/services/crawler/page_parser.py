import logging
import re
import json
from typing import Set, Dict, Any, List, Optional
from bs4 import BeautifulSoup, Tag

from app.services.crawler.url_utils import UrlUtils
from app.config import URL_KEYS, MEDIA_KEYS, SKIP_JSON_KEYS, URL_MEDIA_ATTRIBUTES

logger = logging.getLogger(__name__)

class PageParser:

    def __init__(self):

        self.url_utils = UrlUtils()

        self.css_url_regex = re.compile(r'url\([\'"]?([^\'"()]+)[\'"]?\)')

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> Set[str]:

        links = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                absolute_url = self.url_utils.build_absolute_url(base_url, href)
                if absolute_url:
                    links.add(absolute_url)

        for tag in soup.find_all(attrs={'src': True}):
            src = tag['src'].strip()
            absolute_url = self.url_utils.build_absolute_url(base_url, src)
            if absolute_url:
                links.add(absolute_url)

        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_urls = self.css_url_regex.findall(style_tag.string)
                for css_url in css_urls:
                    absolute_url = self.url_utils.build_absolute_url(base_url, css_url)
                    if absolute_url:
                        links.add(absolute_url)

        return links

    def extract_media_urls(self, soup: BeautifulSoup, base_url: str) -> Set[str]:

        media_urls = set()

        for img in soup.find_all('img', src=True):

            src = img['src'].strip()
            if src:
                absolute_url = self.url_utils.build_absolute_url(base_url, src)
                if absolute_url:
                    media_urls.add(absolute_url)

            srcset = img.get('srcset', '')
            if srcset:
                for src_item in srcset.split(','):
                    parts = src_item.strip().split(' ')
                    if parts:
                        src = parts[0].strip()
                        absolute_url = self.url_utils.build_absolute_url(base_url, src)
                        if absolute_url:
                            media_urls.add(absolute_url)

        for media_tag in soup.find_all(['video', 'audio', 'source']):

            src = media_tag.get('src', '')
            if src:
                absolute_url = self.url_utils.build_absolute_url(base_url, src)
                if absolute_url:
                    media_urls.add(absolute_url)

            if media_tag.name == 'video':
                poster = media_tag.get('poster', '')
                if poster:
                    absolute_url = self.url_utils.build_absolute_url(base_url, poster)
                    if absolute_url:
                        media_urls.add(absolute_url)

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if href and self.url_utils.is_media_url(href):
                absolute_url = self.url_utils.build_absolute_url(base_url, href)
                if absolute_url:
                    media_urls.add(absolute_url)

        for tag in soup.find_all(style=True):
            style = tag['style']
            urls = self.css_url_regex.findall(style)
            for url in urls:
                absolute_url = self.url_utils.build_absolute_url(base_url, url)
                if absolute_url and self.url_utils.is_media_url(absolute_url):
                    media_urls.add(absolute_url)

        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_urls = self.css_url_regex.findall(style_tag.string)
                for css_url in css_urls:
                    if self.url_utils.is_media_url(css_url):
                        absolute_url = self.url_utils.build_absolute_url(base_url, css_url)
                        if absolute_url:
                            media_urls.add(absolute_url)

        return media_urls

    def extract_media_from_json(self, data: Any, base_url: str) -> Set[str]:

        media_urls = set()

        try:
            self._process_json_data(data, base_url, media_urls)
        except Exception as e:
            logger.warning(f"Error extracting media from JSON: {e}")

        return media_urls

    def _process_json_data(self, data: Any, base_url: str, media_urls: Set[str], path: str = ''):

        if isinstance(data, dict):
            for key, value in data.items():

                if any(sk in key.lower() for sk in SKIP_JSON_KEYS):
                    continue

                current_path = f"{path}.{key}" if path else key

                if isinstance(value, str):
                    self._process_potential_url(key, value, base_url, media_urls)

                elif isinstance(value, dict):
                    self._process_json_data(value, base_url, media_urls, current_path)
                elif isinstance(value, list):
                    self._process_json_data(value, base_url, media_urls, current_path)

        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"

                if isinstance(item, str):
                    self._process_potential_url_in_list(item, base_url, media_urls)

                elif isinstance(item, dict) or isinstance(item, list):
                    self._process_json_data(item, base_url, media_urls, current_path)

    def _process_potential_url(self, key: str, value: str, base_url: str, media_urls: Set[str]):

        if self._is_potential_url_key(key):

            absolute_url = self.url_utils.build_absolute_url(base_url, value)
            if absolute_url and self.url_utils.is_media_url(absolute_url):
                media_urls.add(absolute_url)

    def _is_potential_url_key(self, key: str) -> bool:

        key_lower = key.lower()
        return any(k in key_lower for k in URL_KEYS) or any(k in key_lower for k in MEDIA_KEYS)

    def _process_potential_url_in_list(self, value: str, base_url: str, media_urls: Set[str]):

        if '://' in value or value.startswith('/'):
            absolute_url = self.url_utils.build_absolute_url(base_url, value)
            if absolute_url and self.url_utils.is_media_url(absolute_url):
                media_urls.add(absolute_url)