import aiohttp
import asyncio
import logging

from typing import Dict, Any, Optional, Tuple

from app.config import REQUEST_TIMEOUT
from app.utils.http.session import get_standard_headers

logger = logging.getLogger(__name__)

async def fetch_url(
    session: aiohttp.ClientSession,
    url: str,
    method: str = 'GET',
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = REQUEST_TIMEOUT,
    allow_redirects: bool = True,
    max_retries: int = 2,
    retry_delay: int = 1
) -> Tuple[int, Optional[str], Optional[Dict[str, str]]]:

    if headers is None:
        headers = get_standard_headers()

    retries = 0
    while retries <= max_retries:
        try:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout,
                allow_redirects=allow_redirects
            ) as response:

                try:
                    content = await response.text()
                except UnicodeDecodeError:

                    content = None
                    logger.warning(f"Could not decode response content as text for {url}")

                return response.status, content, dict(response.headers)

        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {url} (attempt {retries+1}/{max_retries+1})")
        except aiohttp.ClientError as e:
            logger.warning(f"Error fetching {url}: {e} (attempt {retries+1}/{max_retries+1})")
        except Exception as e:
            logger.warning(f"Unexpected error fetching {url}: {e} (attempt {retries+1}/{max_retries+1})")

        retries += 1

        if retries > max_retries:
            break

        await asyncio.sleep(retry_delay)

    return 0, None, None

async def download_file(
    session: aiohttp.ClientSession,
    url: str,
    destination_path: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = REQUEST_TIMEOUT,
    chunk_size: int = 64 * 1024,
    max_retries: int = 2,
    retry_delay: int = 1
) -> Tuple[bool, Optional[str], int]:

    import os
    import aiofiles

    if headers is None:
        headers = {}

    retries = 0
    while retries <= max_retries:
        try:
            async with session.get(
                url=url,
                headers=headers,
                timeout=timeout
            ) as response:
                if response.status != 200:
                    logger.warning(f"Failed to download {url}: HTTP {response.status}")
                    retries += 1
                    if retries <= max_retries:
                        await asyncio.sleep(retry_delay)
                    continue

                content_type = response.headers.get('Content-Type', '')

                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                file_size = 0
                async with aiofiles.open(destination_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
                        file_size += len(chunk)

                return True, content_type, file_size

        except asyncio.TimeoutError:
            logger.warning(f"Timeout downloading {url} (attempt {retries+1}/{max_retries+1})")
        except aiohttp.ClientError as e:
            logger.warning(f"Error downloading {url}: {e} (attempt {retries+1}/{max_retries+1})")
        except Exception as e:
            logger.warning(f"Unexpected error downloading {url}: {e} (attempt {retries+1}/{max_retries+1})")

            if os.path.exists(destination_path):
                try:
                    os.remove(destination_path)
                except:
                    pass

        retries += 1

        if retries > max_retries:
            break

        await asyncio.sleep(retry_delay)

    return False, None, 0