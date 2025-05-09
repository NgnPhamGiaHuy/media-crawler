import os
import json
import fcntl
import logging
import tempfile

from typing import List, Dict, Any, Optional

from app.models.media import Media

logger = logging.getLogger(__name__)

class MediaMetadataManager:

    def __init__(self, path_manager):
        self.path_manager = path_manager

        self._media_cache = {}

    def save_media_metadata(self, session_id: str, media_list: List[Media]) -> bool:

        if not os.path.exists(self.path_manager.get_session_path(session_id)):
            return False

        metadata_path = self.path_manager.get_media_metadata_path(session_id)
        metadata_dir = os.path.dirname(metadata_path)

        try:

            media_data = []
            for media in media_list:

                media_dict = media.to_dict()

                if media_dict.get('file_path'):
                    media_dict['file_path'] = os.path.basename(media_dict['file_path'])

                if media_dict.get('thumbnail_path'):
                    media_dict['thumbnail_path'] = os.path.basename(media_dict['thumbnail_path'])

                media_data.append(media_dict)

            self._media_cache[session_id] = media_data

            with tempfile.NamedTemporaryFile(mode='w', dir=metadata_dir, delete=False) as temp_file:
                json.dump(media_data, temp_file, indent=2)
                temp_file_path = temp_file.name

            os.replace(temp_file_path, metadata_path)

            return True

        except Exception as e:
            logger.warning(f"Error saving media metadata: {e}")

            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            return False

    def get_media_metadata(self, session_id: str) -> List[Dict[str, Any]]:

        if not os.path.exists(self.path_manager.get_session_path(session_id)):
            return []

        if session_id in self._media_cache:

            media_data = self._process_media_paths(session_id, self._media_cache[session_id])
            return media_data

        metadata_path = self.path_manager.get_media_metadata_path(session_id)

        try:
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:

                    fcntl.flock(f, fcntl.LOCK_SH)
                    try:
                        media_data = json.load(f)

                        self._media_cache[session_id] = media_data

                        return self._process_media_paths(session_id, media_data)
                    except json.JSONDecodeError:
                        logger.warning(f"Corrupted media metadata file for session {session_id}")
                        return []
                    finally:
                        fcntl.flock(f, fcntl.LOCK_UN)

            return []

        except Exception as e:
            logger.warning(f"Error getting media metadata: {e}")
            return []

    def _process_media_paths(self, session_id: str, media_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

        result = []
        session_dir = self.path_manager.get_session_path(session_id)
        thumbnails_dir = self.path_manager.get_thumbnails_dir(session_id)

        for media in media_data:

            media_copy = media.copy()

            if media_copy.get('file_path'):
                media_copy['file_path'] = os.path.join(session_dir, media_copy['file_path'])

            if media_copy.get('thumbnail_path'):
                media_copy['thumbnail_path'] = os.path.join(thumbnails_dir, media_copy['thumbnail_path'])

            result.append(media_copy)

        return result

    def get_media_by_id(self, session_id: str, media_id: str) -> Optional[Dict[str, Any]]:

        media_list = self.get_media_metadata(session_id)

        for media in media_list:
            if media.get('id') == media_id:
                return media

        return None

    def get_media_by_url(self, session_id: str, url: str) -> Optional[Dict[str, Any]]:

        media_list = self.get_media_metadata(session_id)

        for media in media_list:
            if media.get('url') == url:
                return media

        return None