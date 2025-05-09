import logging
import aiohttp

from typing import Tuple, List, Set, Dict, Optional
from datetime import datetime

from app.config import USER_AGENT, MAX_CRAWL_DEPTH
from app.models.crawler import CrawlStats, CrawlSession
from app.services.cache import CacheManager
from app.services.crawler.url_utils import UrlUtils
from app.services.crawler.crawl_engine import CrawlEngine
from app.services.crawler.stats_manager import StatsManager
from app.services.crawler.session_manager import CrawlSessionManager

logger = logging.getLogger(__name__)

class Crawler:

    def __init__(self, session_id: Optional[str] = None):

        self.cache_manager = CacheManager()
        self.session_manager = CrawlSessionManager(self.cache_manager)
        self.stats_manager = StatsManager()
        self.url_utils = UrlUtils()

        self.session_id = session_id

        self.session = None
        self.crawl_engine = None

        self.original_url = None

    async def init_session(self) -> None:

        if self.session is None:
            headers = {'User-Agent': USER_AGENT}
            await self._create_http_session(headers)

    async def _create_http_session(self, headers: Dict[str, str]) -> None:

        try:

            self.session = aiohttp.ClientSession(
                headers=headers,
                connector=aiohttp.TCPConnector(ssl=False)
            )
            self.crawl_engine = CrawlEngine(self.session)
        except Exception as e:
            logger.error(f"Error creating HTTP session: {e}")

            self.session = aiohttp.ClientSession(headers=headers)
            self.crawl_engine = CrawlEngine(self.session)

    async def close(self) -> None:

        if self.session:
            await self.session.close()
            self.session = None
            self.crawl_engine = None

    async def crawl(self, url: str, max_depth: int = MAX_CRAWL_DEPTH) -> Tuple[CrawlStats, List[str]]:

        await self.init_session()
        self.stats_manager.reset()

        try:

            self.original_url = url

            url = self.url_utils.normalize_url(url)

            crawl_session = self._setup_crawl_session(url, max_depth)

            logger.info(f"Starting crawl for {url} with max depth {max_depth}")
            media_urls = await self._perform_crawl(url, max_depth)

            return self._finalize_crawl(crawl_session, media_urls)
        except Exception as e:
            return self._handle_crawl_error(url, e)
        finally:
            await self.close()

    def _setup_crawl_session(self, url: str, max_depth: int) -> Optional[CrawlSession]:

        try:

            if self.session_id and self.cache_manager.session_exists(self.session_id):
                crawl_session = self.session_manager.get_session(self.session_id)

                if not crawl_session:
                    crawl_session = CrawlSession(
                        id=self.session_id,
                        url=url,
                        max_depth=max_depth,
                        status="created",
                        start_time=datetime.now()
                    )
                    self.session_manager._save_session_info(self.session_id, crawl_session)
            else:

                crawl_session = self.session_manager.create_session(url, max_depth)
                self.session_id = crawl_session.id

            self.session_manager.mark_session_started(self.session_id)
            return crawl_session
        except Exception as e:
            logger.error(f"Error setting up crawl session: {e}")
            return None

    async def _perform_crawl(self, url: str, max_depth: int) -> Set[str]:

        return await self.crawl_engine.crawl(url, max_depth)

    def _finalize_crawl(self, crawl_session: Optional[CrawlSession], media_urls: Set[str]) -> Tuple[CrawlStats, List[str]]:

        self.stats_manager.finalize()
        stats = self.stats_manager.get_stats()

        self.session_manager.mark_session_completed(
            self.session_id,
            stats.total_pages,
            len(media_urls)
        )

        self.cache_manager.update_session_metadata(self.session_id, len(media_urls))

        media_urls_list = list(media_urls)

        url_to_log = self.original_url
        if crawl_session and hasattr(crawl_session, 'url') and crawl_session.url:
            url_to_log = crawl_session.url

        logger.info(f"Crawling completed for {url_to_log}. Found {len(media_urls_list)} media URLs.")
        return stats, media_urls_list

    def _handle_crawl_error(self, url: str, error: Exception) -> Tuple[CrawlStats, List[str]]:

        logger.error(f"Error crawling {url}: {error}")

        if self.session_id:
            self.session_manager.mark_session_failed(self.session_id, str(error))

        stats = self.stats_manager.get_stats()
        return stats, []