import aiohttp
import logging

from typing import Dict, Optional

from app.config import USER_AGENT

logger = logging.getLogger(__name__)

async def create_http_session(
    headers: Optional[Dict[str, str]] = None,
    verify_ssl: bool = False
) -> aiohttp.ClientSession:

    if headers is None:
        headers = {}

    if 'User-Agent' not in headers:
        headers['User-Agent'] = USER_AGENT

    try:

        connector_kwargs = {}

        if not verify_ssl:

            connector_kwargs['ssl'] = False

        session = aiohttp.ClientSession(
            headers=headers,
            connector=aiohttp.TCPConnector(**connector_kwargs)
        )

        return session

    except Exception as e:
        logger.error(f"Error creating HTTP session: {e}")

        return aiohttp.ClientSession(headers=headers)

def get_standard_headers() -> Dict[str, str]:

    return {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }