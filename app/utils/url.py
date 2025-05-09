import validators

from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse, urljoin, urlunparse

from app.config import MEDIA_EXTENSIONS

def is_valid_url(url: str) -> bool:

    return validators.url(url) is True

def normalize_url(url: str) -> str:

    try:
        parsed = urlparse(url)

        scheme = parsed.scheme.lower() or 'http'

        netloc = parsed.netloc.lower()

        if ':' in netloc:
            host, port = netloc.split(':', 1)
            if (scheme == 'http' and port == '80') or (scheme == 'https' and port == '443'):
                netloc = host

        path = parsed.path
        if not path:
            path = '/'

        if path != '/' and path.endswith('/'):
            path = path[:-1]

        fragment = ''

        normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, fragment))

        return normalized
    except Exception:

        return url

def get_domain(url: str) -> str:

    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ''

def get_base_url(url: str) -> str:

    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return url

def build_absolute_url(base_url: str, relative_url: str) -> str:

    try:
        return urljoin(base_url, relative_url)
    except Exception:
        return relative_url

def extract_query_params(url: str) -> Dict[str, str]:

    try:
        parsed = urlparse(url)
        query_params = {}

        if parsed.query:
            for param in parsed.query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query_params[key] = value
                else:
                    query_params[param] = ''

        return query_params
    except Exception:
        return {}

def is_same_domain(url1: str, url2: str) -> bool:

    return get_domain(url1) == get_domain(url2)

def strip_url_parameters(url: str) -> str:

    try:
        parsed = urlparse(url)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    except Exception:
        return url

def is_relative_url(url: str) -> bool:

    try:
        return not bool(urlparse(url).netloc)
    except Exception:
        return False

def extract_url_path_segments(url: str) -> List[str]:

    try:
        path = urlparse(url).path

        segments = [segment for segment in path.split('/') if segment]
        return segments
    except Exception:
        return []

def is_media_url(url: str) -> bool:

    try:
        path = Path(urlparse(url).path.lower())
        suffix = path.suffix

        all_media_extensions = []
        for media_type, extensions in MEDIA_EXTENSIONS.items():
            all_media_extensions.extend(extensions)

        return suffix in all_media_extensions
    except Exception:
        return False