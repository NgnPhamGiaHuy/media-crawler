import os
import asyncio
import aiohttp
import logging

from typing import List, Optional, Dict, Any, Set

from app.models.media import Media
from app.services.cache import CacheManager
from app.services.media.mime_utils import MimeTypeUtils
from app.services.media.path_utils import MediaPathUtils
from app.services.media.metadata_generator import MediaMetadataGenerator
from app.services.media.thumbnail_generator import ThumbnailGenerator
from app.services.media.download_handler import DownloadHandler
from app.config import CACHE_DIR, USER_AGENT, MAX_CONCURRENT_DOWNLOADS

logger = logging.getLogger(__name__)

class MediaDownloader:

    def __init__(self, session_id: str = None, cache_dir: str = CACHE_DIR):

        self.cache_manager = CacheManager(cache_dir)

        self.session_id = self._initialize_session(session_id)

        self.cache_dir = self.cache_manager.get_session_path(self.session_id)

        self._initialize_utilities()

        self.downloaded_urls: Set[str] = set()

        self.cache_manager.update_session_access_time(self.session_id)

        logger.info(f"MediaDownloader initialized with session ID: {self.session_id}")
        logger.info(f"Cache directory: {self.cache_dir}")

    def _initialize_session(self, session_id: str) -> str:

        if session_id and self.cache_manager.session_exists(session_id):
            return session_id
        else:
            return self.cache_manager.create_session()

    def _initialize_utilities(self) -> None:

        self.path_utils = MediaPathUtils(self.cache_dir)
        self.mime_utils = MimeTypeUtils()
        self.metadata_generator = MediaMetadataGenerator()
        self.thumbnail_generator = ThumbnailGenerator()

        self.session = None
        self.download_handler = None
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

    async def init_session(self) -> None:

        if self.session is None:
            headers = {'User-Agent': USER_AGENT}
            self._create_http_session(headers)

    def _create_http_session(self, headers: Dict[str, str]) -> None:

        try:

            self.session = aiohttp.ClientSession(
                headers=headers,
                connector=aiohttp.TCPConnector(ssl=False)
            )
            self.download_handler = DownloadHandler(self.session)
        except Exception as e:
            logger.error(f"Error creating HTTP session: {e}")

            self.session = aiohttp.ClientSession(headers=headers)
            self.download_handler = DownloadHandler(self.session)

    async def close(self) -> None:

        if self.session:
            await self.session.close()
            self.session = None
            self.download_handler = None

    def cleanup(self) -> None:

        logger.info(f"Cleaning up cache session: {self.session_id}")
        self.cache_manager.clear_session(self.session_id)

    async def download_media(self, urls: List[str], source_url: str) -> List[Media]:

        await self.init_session()
        results = []

        try:

            tasks = self._create_download_tasks(urls, source_url)

            if tasks:
                results = await self._process_download_tasks(tasks)

            self._update_cache_metadata(results)

            return results
        finally:
            await self.close()

    def _create_download_tasks(self, urls: List[str], source_url: str) -> List[asyncio.Task]:

        tasks = []

        for url in urls:

            if url in self.downloaded_urls:
                logger.debug(f"Skipping duplicate URL: {url}")
                continue

            task = asyncio.create_task(self._download_single_media(url, source_url))
            tasks.append(task)

            self.downloaded_urls.add(url)

        return tasks

    async def _process_download_tasks(self, tasks: List[asyncio.Task]) -> List[Media]:

        results = await asyncio.gather(*tasks)

        return [r for r in results if r is not None]

    def _update_cache_metadata(self, results: List[Media]) -> None:

        if results:
            self.cache_manager.save_media_metadata(self.session_id, results)
            self.cache_manager.update_session_metadata(self.session_id, len(results))
            logger.info(f"Cached {len(results)} media files in session {self.session_id}")
            logger.info(f"Cache directory: {self.cache_dir}")

    async def _download_single_media(self, url: str, source_url: str) -> Optional[Media]:

        cache_path = self.path_utils.get_cache_file_path(url)

        try:
            async with self.semaphore:

                if os.path.exists(cache_path):
                    return await self._process_existing_file(url, source_url, cache_path)

                return await self._download_and_process_file(url, source_url, cache_path)

        except Exception as e:
            logger.warning(f"Error processing media file {url}: {e}")
            self._cleanup_failed_download(cache_path)
            return None

    async def _process_existing_file(self, url: str, source_url: str, cache_path: str) -> Optional[Media]:

        file_size = os.path.getsize(cache_path)
        mime_type = self.mime_utils.get_mime_type(cache_path)
        media_type = self.mime_utils.get_media_type(mime_type)

        if not media_type:

            os.remove(cache_path)
            return None

        logger.info(f"Using cached file for {url}: {cache_path}")

        metadata = await self.metadata_generator.create_metadata(cache_path, mime_type, file_size)

        thumbnail_path = await self._ensure_thumbnail(cache_path, media_type)

        return self._create_media_object(
            url, source_url, cache_path, thumbnail_path,
            media_type, metadata
        )

    async def _download_and_process_file(self, url: str, source_url: str, cache_path: str) -> Optional[Media]:

        success, mime_type, file_size = await self.download_handler.download_file(url, cache_path)

        if not success:
            return None

        media_type = self.mime_utils.get_media_type(mime_type)
        if not media_type:
            self._cleanup_failed_download(cache_path)
            return None

        metadata = await self.metadata_generator.create_metadata(cache_path, mime_type, file_size)

        thumbnail_path = await self._ensure_thumbnail(cache_path, media_type)

        return self._create_media_object(
            url, source_url, cache_path, thumbnail_path,
            media_type, metadata
        )

    async def _ensure_thumbnail(self, cache_path: str, media_type: str) -> Optional[str]:

        thumbnail_path = self.path_utils.get_thumbnail_path(cache_path)
        await self.thumbnail_generator.generate_thumbnail(cache_path, thumbnail_path, media_type)
        return thumbnail_path if os.path.exists(thumbnail_path) else None

    def _create_media_object(self,
                           url: str,
                           source_url: str,
                           file_path: str,
                           thumbnail_path: Optional[str],
                           media_type: str,
                           metadata: Dict[str, Any]) -> Media:

        return Media(
            url=url,
            source_url=source_url,
            file_path=file_path,
            thumbnail_path=thumbnail_path,
            session_id=self.session_id,
            metadata=metadata,
            media_type=media_type
        )

    def _cleanup_failed_download(self, cache_path: str) -> None:

        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
            except Exception as e:
                logger.warning(f"Failed to remove failed download: {e}")