import logging

from pathlib import Path

logger = logging.getLogger(__name__)

class CachePathManager:

    def __init__(self, base_cache_dir):
        self.base_cache_dir = self.resolve_cache_dir(base_cache_dir)

        self.base_cache_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"CachePathManager initialized with base directory: {self.base_cache_dir}")

    def resolve_cache_dir(self, base_cache_dir):

        if base_cache_dir == '@cachefolder':

            app_dir = Path(__file__).parent.parent.parent.parent

            cache_dir = app_dir / 'cache'
            logger.info(f"Using @cachefolder path: {cache_dir}")
            return cache_dir
        return Path(base_cache_dir)

    def get_session_path(self, session_id):

        path = self.base_cache_dir / session_id
        return str(path)

    def get_metadata_path(self, session_id):

        session_path = self.get_session_path(session_id)
        return f"{session_path}/metadata.json"

    def get_media_metadata_path(self, session_id):

        session_path = self.get_session_path(session_id)
        return f"{session_path}/media.json"

    def get_thumbnails_dir(self, session_id):

        session_path = self.get_session_path(session_id)
        return f"{session_path}/thumbnails"

    def get_crawl_session_path(self, session_id):

        session_path = self.get_session_path(session_id)
        return f"{session_path}/crawl_session.json"