import uuid
import hashlib
import logging

from pathlib import Path
from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)

class MediaPathUtils:

    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)

    def get_cache_file_path(self, url: str) -> str:

        parsed = urlparse(url)
        filename = Path(unquote(parsed.path)).name

        if not filename:
            filename = f"{hashlib.md5(url.encode()).hexdigest()}"

        path = Path(filename)
        base = path.stem
        ext = path.suffix or '.bin'

        base = ''.join(c for c in base if c.isalnum() or c in '_-.')

        unique_filename = f"{base}_{str(uuid.uuid4().hex[:8])}{ext}"

        return str(self.cache_dir / unique_filename)

    def get_thumbnail_path(self, media_path: str) -> str:

        path = Path(media_path)
        filename = path.name
        base = path.stem
        thumbnails_dir = self.cache_dir / 'thumbnails'

        thumbnails_dir.mkdir(exist_ok=True, parents=True)

        return str(thumbnails_dir / f"{base}_thumb.jpg")