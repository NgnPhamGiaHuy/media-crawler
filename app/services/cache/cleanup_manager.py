import os
import shutil
import json
import time
import logging

logger = logging.getLogger(__name__)

class CleanupManager:

    def __init__(self, path_manager):
        self.path_manager = path_manager

    def clear_session(self, session_id: str) -> bool:

        session_path = self.path_manager.get_session_path(session_id)
        if not os.path.exists(session_path):
            return False

        lock_file = os.path.join(session_path, ".cleanup_lock")

        try:

            with open(lock_file, 'w') as f:
                f.write(f"cleanup_started:{time.time()}")

            time.sleep(0.1)

            shutil.rmtree(session_path)
            logger.info(f"Cleared cache session: {session_id}")
            return True
        except Exception as e:
            logger.warning(f"Error clearing session {session_id}: {e}")

            try:
                if os.path.exists(lock_file):
                    os.remove(lock_file)
            except:
                pass
            return False

    def clean_expired_sessions(self, expiry_time: int = 3600) -> int:

        now = time.time()
        sessions_cleared = 0

        try:

            for item in os.listdir(self.path_manager.base_cache_dir):
                session_dir = os.path.join(self.path_manager.base_cache_dir, item)

                if not os.path.isdir(session_dir):
                    continue

                metadata_path = os.path.join(session_dir, 'metadata.json')
                if not os.path.exists(metadata_path):

                    logger.info(f"Removing session with no metadata: {item}")
                    self.clear_session(item)
                    sessions_cleared += 1
                    continue

                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)

                    last_accessed = metadata.get('last_accessed', 0)

                    if expiry_time == 0 or (now - last_accessed > expiry_time):
                        logger.info(f"Removing expired session: {item}")
                        self.clear_session(item)
                        sessions_cleared += 1

                except Exception as e:
                    logger.warning(f"Error reading metadata for session {item}: {e}")

                    self.clear_session(item)
                    sessions_cleared += 1

        except Exception as e:
            logger.error(f"Error cleaning expired sessions: {e}")

        logger.info(f"Cleaned {sessions_cleared} expired sessions")
        return sessions_cleared

    def get_cache_size(self) -> int:

        total_size = 0

        try:

            base_cache_dir = str(self.path_manager.base_cache_dir)

            for dirpath, dirnames, filenames in os.walk(base_cache_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.error(f"Error calculating cache size: {e}")

        return total_size