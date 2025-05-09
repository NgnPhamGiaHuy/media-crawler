import aiohttp
import logging

from typing import Dict, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from app.config import USER_AGENT, RESPECT_ROBOTS_TXT

logger = logging.getLogger(__name__)

class RobotsParser:

    def __init__(self, session: aiohttp.ClientSession):

        self.session = session
        self.robots_cache: Dict[str, RobotFileParser] = {}

    async def is_allowed(self, url: str) -> bool:

        if not RESPECT_ROBOTS_TXT:
            return True

        try:

            parsed = urlparse(url)

            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            parser = await self._get_robots_parser(robots_url)

            if parser:
                return parser.can_fetch(USER_AGENT, url)

            return True
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")

            return True

    async def _get_robots_parser(self, robots_url: str) -> Optional[RobotFileParser]:

        if robots_url in self.robots_cache:
            return self.robots_cache[robots_url]

        try:
            parser = RobotFileParser(robots_url)

            async with self.session.get(robots_url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    parser.parse(content.splitlines())
                    self.robots_cache[robots_url] = parser
                    return parser
                else:

                    logger.debug(f"No robots.txt found at {robots_url} (status: {response.status})")

                    empty_parser = RobotFileParser()
                    empty_parser.parse([])
                    self.robots_cache[robots_url] = empty_parser
                    return empty_parser
        except Exception as e:
            logger.warning(f"Error fetching robots.txt from {robots_url}: {e}")

            empty_parser = RobotFileParser()
            empty_parser.parse([])
            self.robots_cache[robots_url] = empty_parser
            return empty_parser