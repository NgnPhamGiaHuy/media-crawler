import asyncio
import aiohttp
import logging

from bs4 import BeautifulSoup
from datetime import datetime
from typing import Set, Tuple, List

from app.models.crawler import CrawlPage
from app.services.crawler.url_utils import UrlUtils
from app.services.crawler.page_parser import PageParser
from app.services.crawler.robots_parser import RobotsParser
from app.config import REQUEST_TIMEOUT, MAX_CONCURRENT_REQUESTS

logger = logging.getLogger(__name__)

class CrawlEngine:

    def __init__(self, session: aiohttp.ClientSession):

        self.session = session
        self.url_utils = UrlUtils()
        self.robots_parser = RobotsParser(session)
        self.page_parser = PageParser()
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.visited_urls: Set[str] = set()
        self.media_urls: Set[str] = set()

    async def crawl_page(self, url: str, depth: int, max_depth: int) -> CrawlPage:

        if not url:
            logger.warning("Attempted to crawl with empty URL")
            return CrawlPage(
                url="<empty>",
                depth=depth,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message="Empty URL provided"
            )

        crawl_page = CrawlPage(
            url=url,
            depth=depth,
            start_time=datetime.now()
        )

        if self._should_skip_url(url, depth, max_depth):
            crawl_page.end_time = datetime.now()
            return crawl_page

        self.visited_urls.add(url)

        if not await self._is_allowed_by_robots(url, crawl_page):
            return crawl_page

        try:

            return await self._fetch_and_process_page(url, crawl_page)
        except asyncio.TimeoutError:
            logger.warning(f"Timeout crawling {url}")
            crawl_page.error_message = "Request timeout"
            crawl_page.end_time = datetime.now()
            return crawl_page
        except Exception as e:
            logger.warning(f"Error crawling {url}: {e}")
            crawl_page.error_message = str(e)
            crawl_page.end_time = datetime.now()
            return crawl_page

    def _should_skip_url(self, url: str, depth: int, max_depth: int) -> bool:

        if url in self.visited_urls:
            return True

        if depth > max_depth:
            return True

        return False

    async def _is_allowed_by_robots(self, url: str, crawl_page: CrawlPage) -> bool:

        try:
            if not await self.robots_parser.is_allowed(url):
                logger.debug(f"Skipping {url}: disallowed by robots.txt")
                crawl_page.error_message = "Disallowed by robots.txt"
                crawl_page.end_time = datetime.now()
                return False
            return True
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")

            return True

    async def _fetch_and_process_page(self, url: str, crawl_page: CrawlPage) -> CrawlPage:

        async with self.semaphore:

            try:
                async with self.session.get(url, timeout=REQUEST_TIMEOUT) as response:
                    crawl_page.status_code = response.status

                    if response.status != 200:
                        logger.debug(f"Skipping {url}: HTTP {response.status}")
                        crawl_page.error_message = f"HTTP {response.status}"
                        crawl_page.end_time = datetime.now()
                        return crawl_page

                    content_type = response.headers.get('Content-Type', '').lower()
                    await self._process_by_content_type(response, content_type, url, crawl_page)

                    crawl_page.end_time = datetime.now()
                    return crawl_page
            except aiohttp.ClientError as e:
                logger.warning(f"HTTP client error for {url}: {e}")
                crawl_page.error_message = f"HTTP client error: {str(e)}"
                crawl_page.end_time = datetime.now()
                return crawl_page

    async def _process_by_content_type(self,
                                      response: aiohttp.ClientResponse,
                                      content_type: str,
                                      url: str,
                                      crawl_page: CrawlPage) -> None:

        try:
            if 'text/html' in content_type:
                await self._process_html_page(response, url, crawl_page)
            elif 'application/json' in content_type:
                await self._process_json_response(response, url, crawl_page)

        except Exception as e:
            logger.warning(f"Error processing content type {content_type} for {url}: {e}")
            crawl_page.error_message = f"Error processing content: {str(e)}"

    async def _process_html_page(self,
                               response: aiohttp.ClientResponse,
                               url: str,
                               crawl_page: CrawlPage) -> None:

        try:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            links = self.page_parser.extract_links(soup, url)
            media = self.page_parser.extract_media_urls(soup, url)

            crawl_page.discovered_urls = links
            crawl_page.media_urls = media

            self.media_urls.update(media)
        except Exception as e:
            logger.warning(f"Error processing HTML for {url}: {e}")
            crawl_page.error_message = f"Error processing HTML: {str(e)}"

    async def _process_json_response(self,
                                   response: aiohttp.ClientResponse,
                                   url: str,
                                   crawl_page: CrawlPage) -> None:

        try:
            json_data = await response.json()
            media = self.page_parser.extract_media_from_json(json_data, url)

            crawl_page.media_urls = media

            self.media_urls.update(media)
        except Exception as e:
            logger.warning(f"Error processing JSON for {url}: {e}")
            crawl_page.error_message = f"Error processing JSON: {str(e)}"

    async def crawl(self, url: str, max_depth: int) -> Set[str]:

        if not url:
            logger.error("Cannot crawl empty URL")
            return set()

        self._reset_crawl_state()
        to_crawl = self._initialize_crawl_queue(url)

        try:
            await self._process_crawl_queue(to_crawl, max_depth, url)
        except Exception as e:
            logger.error(f"Error during crawl queue processing: {e}")

        return self.media_urls

    def _reset_crawl_state(self) -> None:

        self.visited_urls.clear()
        self.media_urls.clear()

    def _initialize_crawl_queue(self, start_url: str) -> List[Tuple[str, int]]:

        return [(start_url, 0)]

    async def _process_crawl_queue(self,
                                to_crawl: List[Tuple[str, int]],
                                max_depth: int,
                                base_url: str) -> None:

        while to_crawl:
            try:

                current_url, current_depth = to_crawl.pop(0)

                if current_url in self.visited_urls:
                    continue

                crawl_page = await self.crawl_page(current_url, current_depth, max_depth)

                if self._should_follow_links(crawl_page, current_depth, max_depth):
                    self._add_new_urls_to_queue(crawl_page.discovered_urls, current_depth, to_crawl, base_url)
            except Exception as e:
                logger.error(f"Error processing URL in queue: {e}")

    def _should_follow_links(self, crawl_page: CrawlPage, current_depth: int, max_depth: int) -> bool:

        return crawl_page and crawl_page.is_successful and current_depth < max_depth

    def _add_new_urls_to_queue(self,
                              discovered_urls: Set[str],
                              current_depth: int,
                              to_crawl: List[Tuple[str, int]],
                              base_url: str) -> None:

        if not discovered_urls:
            return

        try:

            same_domain_urls = self.url_utils.filter_same_domain_urls(
                discovered_urls, base_url
            )

            for discovered_url in same_domain_urls:
                if discovered_url not in self.visited_urls:
                    to_crawl.append((discovered_url, current_depth + 1))
        except Exception as e:
            logger.warning(f"Error adding URLs to crawl queue: {e}")
