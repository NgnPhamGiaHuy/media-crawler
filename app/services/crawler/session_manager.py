import json
import logging

from typing import Optional
from pathlib import Path
from datetime import datetime

from app.models.crawler import CrawlSession
from app.services.cache import CacheManager

logger = logging.getLogger(__name__)

class CrawlSessionManager:

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager

    def create_session(self, url: str, max_depth: int) -> CrawlSession:

        session_id = self.cache_manager.create_session()

        crawl_session = CrawlSession(
            id=session_id,
            url=url,
            max_depth=max_depth,
            status="created",
            start_time=datetime.now()
        )

        self._save_session_info(session_id, crawl_session)

        logger.info(f"Created new crawl session: {session_id} for URL: {url}")
        return crawl_session

    def get_session(self, session_id: str) -> Optional[CrawlSession]:

        if not self.cache_manager.session_exists(session_id):
            return None

        session_path = Path(self.cache_manager.get_session_path(session_id))
        crawl_info_path = session_path / 'crawl_session.json'

        if not crawl_info_path.exists():

            return None

        try:

            with open(str(crawl_info_path), 'r') as f:
                data = json.load(f)

            crawl_session = CrawlSession(
                id=session_id,
                url=data.get('url', ''),
                max_depth=data.get('max_depth', 1)
            )

            if 'start_time' in data:
                crawl_session.start_time = datetime.fromisoformat(data['start_time'])

            if 'end_time' in data and data['end_time']:
                crawl_session.end_time = datetime.fromisoformat(data['end_time'])

            crawl_session.status = data.get('status', 'unknown')
            crawl_session.error_message = data.get('error_message')
            crawl_session.pages_crawled = data.get('pages_crawled', 0)
            crawl_session.media_found = data.get('media_found', 0)

            return crawl_session

        except Exception as e:
            logger.warning(f"Error loading crawl session {session_id}: {e}")
            return None

    def update_session(self, session: CrawlSession) -> bool:

        return self._save_session_info(session.id, session)

    def mark_session_started(self, session_id: str) -> bool:

        session = self.get_session(session_id)
        if not session:
            return False

        session.status = "running"
        session.start_time = datetime.now()

        return self.update_session(session)

    def mark_session_completed(self, session_id: str, pages_crawled: int, media_found: int) -> bool:

        session = self.get_session(session_id)
        if not session:
            return False

        session.status = "completed"
        session.end_time = datetime.now()
        session.pages_crawled = pages_crawled
        session.media_found = media_found

        return self.update_session(session)

    def mark_session_failed(self, session_id: str, error_message: str) -> bool:

        session = self.get_session(session_id)
        if not session:
            return False

        session.status = "error"
        session.end_time = datetime.now()
        session.error_message = error_message

        return self.update_session(session)

    def _save_session_info(self, session_id: str, session: CrawlSession) -> bool:

        if not self.cache_manager.session_exists(session_id):
            return False

        session_path = Path(self.cache_manager.get_session_path(session_id))
        crawl_info_path = str(session_path / 'crawl_session.json')

        try:

            data = session.to_dict()

            with open(crawl_info_path, 'w') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            logger.warning(f"Error saving crawl session {session_id}: {e}")
            return False