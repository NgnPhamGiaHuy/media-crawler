from app.services.cache.path_manager import CachePathManager
from app.services.cache.session_manager import SessionManager
from app.services.cache.cleanup_manager import CleanupManager
from app.services.cache.media_metadata import MediaMetadataManager

__all__ = ['CacheManager']

class CacheManager:
    def __init__(self, base_cache_dir='@cachefolder'):
        self.path_manager = CachePathManager(base_cache_dir)
        self.session_manager = SessionManager(self.path_manager)
        self.media_metadata = MediaMetadataManager(self.path_manager)
        self.cleanup_manager = CleanupManager(self.path_manager)

    def get_session_path(self, session_id):
        return self.path_manager.get_session_path(session_id)

    def create_session(self):
        return self.session_manager.create_session()

    def session_exists(self, session_id):
        return self.session_manager.session_exists(session_id)

    def update_session_access_time(self, session_id):
        return self.session_manager.update_session_access_time(session_id)

    def update_session_metadata(self, session_id, media_count):
        return self.session_manager.update_session_metadata(session_id, media_count)

    def get_session_stats(self, session_id):
        return self.session_manager.get_session_stats(session_id)

    def save_media_metadata(self, session_id, media_list):
        return self.media_metadata.save_media_metadata(session_id, media_list)

    def get_media_metadata(self, session_id):
        return self.media_metadata.get_media_metadata(session_id)

    def get_media_by_id(self, session_id, media_id):
        return self.media_metadata.get_media_by_id(session_id, media_id)

    def get_media_by_url(self, session_id, url):
        return self.media_metadata.get_media_by_url(session_id, url)

    def clear_session(self, session_id):
        return self.cleanup_manager.clear_session(session_id)

    def clean_expired_sessions(self, expiry_time=3600):
        return self.cleanup_manager.clean_expired_sessions(expiry_time)

    def get_cache_size(self):
        return self.cleanup_manager.get_cache_size()