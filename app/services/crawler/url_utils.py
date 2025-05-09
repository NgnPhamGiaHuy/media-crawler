import logging
import validators

from pathlib import Path
from typing import Set, Optional
from urllib.parse import urlparse, urljoin, urlunparse

from app.config import MEDIA_EXTENSIONS

logger = logging.getLogger(__name__)

class UrlUtils:

    @staticmethod
    def get_domain(url: str) -> str:

        parsed = urlparse(url)
        return parsed.netloc

    @staticmethod
    def normalize_url(url: str) -> str:

        parsed = urlparse(url)

        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''
        ))

        if normalized.endswith('/') and parsed.path != '/':
            normalized = normalized[:-1]

        return normalized

    @staticmethod
    def is_same_domain(url1: str, url2: str) -> bool:

        domain1 = UrlUtils.get_domain(url1)
        domain2 = UrlUtils.get_domain(url2)
        return domain1 == domain2

    @staticmethod
    def is_valid_url(url: str) -> bool:

        return validators.url(url) is True

    @staticmethod
    def build_absolute_url(base_url: str, relative_url: str) -> Optional[str]:

        try:
            absolute_url = urljoin(base_url, relative_url)
            if UrlUtils.is_valid_url(absolute_url):
                return UrlUtils.normalize_url(absolute_url)
            return None
        except Exception as e:
            logger.debug(f"Error building absolute URL from {base_url} and {relative_url}: {e}")
            return None

    @staticmethod
    def filter_same_domain_urls(urls: Set[str], base_url: str) -> Set[str]:

        base_domain = UrlUtils.get_domain(base_url)
        return {url for url in urls if UrlUtils.get_domain(url) == base_domain}

    @staticmethod
    def is_media_url(url: str) -> bool:

        parsed = urlparse(url)
        path = Path(parsed.path.lower())
        suffix = path.suffix

        all_media_extensions = []
        for media_type, extensions in MEDIA_EXTENSIONS.items():
            all_media_extensions.extend(extensions)

        return suffix in all_media_extensions