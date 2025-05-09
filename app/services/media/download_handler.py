import logging
import asyncio
import aiohttp
import aiofiles

from pathlib import Path
from typing import Optional, Tuple

from app.config import REQUEST_TIMEOUT, MAX_IMAGE_SIZE, MAX_VIDEO_SIZE, MAX_AUDIO_SIZE
from app.services.media.mime_utils import MimeTypeUtils

logger = logging.getLogger(__name__)

class DownloadHandler:

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.mime_utils = MimeTypeUtils()

    async def download_file(self, url: str, file_path: str) -> Tuple[bool, Optional[str], int]:

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:

            async with self.session.get(url, timeout=REQUEST_TIMEOUT) as response:
                if response.status != 200:
                    logger.warning(f"Failed to download {url}: HTTP {response.status}")
                    return False, None, 0

                content_type = response.headers.get('Content-Type', '').lower()
                media_type = self.mime_utils.get_media_type(content_type)

                if not media_type:
                    logger.debug(f"Skipping non-media URL: {url} (Content-Type: {content_type})")
                    return False, None, 0

                content_length = response.headers.get('Content-Length')
                if content_length:
                    try:
                        file_size = int(content_length)

                        if self._is_file_too_large(file_size, media_type):
                            logger.warning(f"File too large: {url} ({file_size} bytes)")
                            return False, None, 0
                    except ValueError:

                        pass

                async with aiofiles.open(path, 'wb') as f:
                    file_size = 0
                    chunk_size = 1024 * 64

                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
                        file_size += len(chunk)

                        if self._is_file_too_large(file_size, media_type):
                            logger.warning(f"File too large during download: {url} ({file_size} bytes)")
                            await f.close()
                            path.unlink(missing_ok=True)
                            return False, None, 0

                mime_type = self.mime_utils.get_mime_type(str(path))
                actual_media_type = self.mime_utils.get_media_type(mime_type)

                if not actual_media_type:
                    logger.debug(f"File is not a media file: {url} (MIME: {mime_type})")
                    path.unlink(missing_ok=True)
                    return False, None, 0

                logger.info(f"Downloaded {url} to {path} ({file_size} bytes)")
                return True, mime_type, file_size

        except asyncio.TimeoutError:
            logger.warning(f"Timeout downloading {url}")
            if path.exists():
                path.unlink()
            return False, None, 0

        except Exception as e:
            logger.warning(f"Error downloading {url}: {e}")
            if path.exists():
                path.unlink()
            return False, None, 0

    def _is_file_too_large(self, file_size: int, media_type: str) -> bool:

        if media_type == 'image' and file_size > MAX_IMAGE_SIZE:
            return True
        elif media_type == 'video' and file_size > MAX_VIDEO_SIZE:
            return True
        elif media_type == 'audio' and file_size > MAX_AUDIO_SIZE:
            return True
        return False