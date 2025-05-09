import magic
import logging

from typing import Optional

from app.config import MEDIA_TYPES

logger = logging.getLogger(__name__)

class MimeTypeUtils:

    @staticmethod
    def get_mime_type(file_path: str) -> str:

        try:

            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(file_path)
            return mime_type
        except Exception as e:
            logger.warning(f"Error detecting MIME type: {e}")
            return "application/octet-stream"

    @staticmethod
    def get_media_type(mime_type: str) -> Optional[str]:

        if not mime_type:
            return None

        mime_lower = mime_type.lower()

        for media_type, mime_list in MEDIA_TYPES.items():
            if any(mime in mime_lower for mime in mime_list):
                return media_type

        return None