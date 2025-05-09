import os
import json
import time
import uuid
import fcntl
import logging
import tempfile

from typing import Dict, Any

logger = logging.getLogger(__name__)

class SessionManager:

    def __init__(self, path_manager):
        self.path_manager = path_manager

        self._metadata_cache = {}

    def create_session(self) -> str:

        session_id = str(uuid.uuid4())
        session_dir = self.path_manager.get_session_path(session_id)

        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(self.path_manager.get_thumbnails_dir(session_id), exist_ok=True)

        metadata = {
            'created_at': time.time(),
            'last_accessed': time.time(),
            'media_count': 0
        }

        self._metadata_cache[session_id] = metadata

        self._write_metadata_safely(session_id, metadata)

        logger.info(f"Created new cache session: {session_id}")
        return session_id

    def session_exists(self, session_id: str) -> bool:

        session_path = self.path_manager.get_session_path(session_id)

        if not os.path.exists(session_path):
            return False

        lock_file = os.path.join(session_path, ".cleanup_lock")
        if os.path.exists(lock_file):
            logger.debug(f"Session {session_id} is being cleaned up, considering it as non-existent")
            return False

        return True

    def update_session_access_time(self, session_id: str) -> bool:

        if not self.session_exists(session_id):
            return False

        session_dir = self.path_manager.get_session_path(session_id)
        if not os.path.exists(session_dir):
            logger.debug(f"Session directory {session_dir} no longer exists, skipping metadata update")
            return False

        try:

            if session_id in self._metadata_cache:
                metadata = self._metadata_cache[session_id].copy()
            else:

                metadata = self._read_metadata_safely(session_id)
                if metadata is None:

                    metadata = {
                        'created_at': time.time(),
                        'last_accessed': time.time(),
                        'media_count': 0
                    }

            metadata['last_accessed'] = time.time()

            self._metadata_cache[session_id] = metadata

            return self._write_metadata_safely(session_id, metadata)

        except Exception as e:
            logger.warning(f"Error updating session access time: {e}")
            return False

    def update_session_metadata(self, session_id: str, media_count: int) -> bool:

        if not self.session_exists(session_id):
            return False

        session_dir = self.path_manager.get_session_path(session_id)
        if not os.path.exists(session_dir):
            logger.debug(f"Session directory {session_dir} no longer exists, skipping metadata update")
            return False

        try:

            if session_id in self._metadata_cache:
                metadata = self._metadata_cache[session_id].copy()
            else:

                metadata = self._read_metadata_safely(session_id)
                if metadata is None:

                    metadata = {
                        'created_at': time.time(),
                        'last_accessed': time.time(),
                        'media_count': 0
                    }

            metadata['last_accessed'] = time.time()
            metadata['media_count'] = media_count

            self._metadata_cache[session_id] = metadata

            return self._write_metadata_safely(session_id, metadata)

        except Exception as e:
            logger.warning(f"Error updating session metadata: {e}")
            return False

    def _read_metadata_safely(self, session_id: str) -> Dict[str, Any]:

        metadata_path = self.path_manager.get_metadata_path(session_id)

        if not os.path.exists(metadata_path):
            return None

        try:
            with open(metadata_path, 'r') as f:

                try:
                    fcntl.flock(f, fcntl.LOCK_SH)
                    try:
                        metadata = json.load(f)
                        return metadata
                    except json.JSONDecodeError:
                        logger.warning(f"Corrupted metadata file for session {session_id}, will create new metadata")
                        return None
                    finally:

                        fcntl.flock(f, fcntl.LOCK_UN)
                except IOError as e:

                    if not os.path.exists(metadata_path):
                        logger.debug(f"Metadata file {metadata_path} no longer exists during read operation")
                    return None
        except FileNotFoundError:

            logger.debug(f"Metadata file {metadata_path} not found")
            return None
        except Exception as e:
            logger.warning(f"Error reading metadata file: {e}")
            return None

    def _write_metadata_safely(self, session_id: str, metadata: Dict[str, Any]) -> bool:

        metadata_path = self.path_manager.get_metadata_path(session_id)
        metadata_dir = os.path.dirname(metadata_path)

        if not os.path.exists(metadata_dir):
            logger.debug(f"Session directory {metadata_dir} no longer exists, skipping metadata write")
            return False

        try:

            with tempfile.NamedTemporaryFile(mode='w', dir=metadata_dir, delete=False) as temp_file:

                json.dump(metadata, temp_file, indent=2)
                temp_file_path = temp_file.name

            if not os.path.exists(metadata_dir):

                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                logger.debug(f"Session directory {metadata_dir} was removed during metadata write")
                return False

            os.replace(temp_file_path, metadata_path)
            return True

        except Exception as e:
            logger.warning(f"Error writing metadata file: {e}")

            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            return False

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:

        result = {
            'media_count': 0,
            'disk_usage': 0
        }

        if not self.session_exists(session_id):
            return result

        session_path = self.path_manager.get_session_path(session_id)

        if session_id in self._metadata_cache:
            metadata = self._metadata_cache[session_id]

            for key in ['created_at', 'last_accessed', 'media_count']:
                if key in metadata:
                    result[key] = metadata[key]
        else:

            metadata = self._read_metadata_safely(session_id)
            if metadata:

                self._metadata_cache[session_id] = metadata

                for key in ['created_at', 'last_accessed', 'media_count']:
                    if key in metadata:
                        result[key] = metadata[key]

        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(session_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)

            result['disk_usage'] = total_size
        except Exception as e:
            logger.warning(f"Error calculating disk usage: {e}")

        try:
            media_files = []
            media_types = {}

            media_metadata_path = self.path_manager.get_media_metadata_path(session_id)
            if os.path.exists(media_metadata_path):
                try:
                    with open(media_metadata_path, 'r') as f:
                        fcntl.flock(f, fcntl.LOCK_SH)
                        try:
                            media_files = json.load(f)
                        except json.JSONDecodeError:
                            logger.warning(f"Corrupted media metadata file for session {session_id}")
                            media_files = []
                        finally:
                            fcntl.flock(f, fcntl.LOCK_UN)

                    for media in media_files:
                        media_type = media.get('media_type', 'unknown')
                        media_types[media_type] = media_types.get(media_type, 0) + 1

                    result['media_types'] = media_types
                    result['media_count'] = len(media_files)
                except Exception as e:
                    logger.warning(f"Error reading media metadata: {e}")
        except Exception as e:
            logger.warning(f"Error analyzing media types: {e}")

        return result