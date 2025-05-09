import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CACHE_DIR = os.getenv('CACHE_DIR', '@cachefolder')
CACHE_EXPIRY = int(os.getenv('CACHE_EXPIRY', 3600))

MAX_CRAWL_DEPTH = int(os.getenv('MAX_CRAWL_DEPTH', 0))
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 5))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
RESPECT_ROBOTS_TXT = os.getenv('RESPECT_ROBOTS_TXT', 'True').lower() in ('true', '1', 't')
USER_AGENT = os.getenv('USER_AGENT', 'MediaCrawler/1.0 (+https://github.com/yourusername/media-crawler)')

MAX_CONCURRENT_DOWNLOADS = int(os.getenv('MAX_CONCURRENT_DOWNLOADS', 10))

ALLOWED_MEDIA_TYPES = os.getenv('ALLOWED_MEDIA_TYPES', 'image,video,audio').split(',')

MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 10 * 1024 * 1024))
MAX_VIDEO_SIZE = int(os.getenv('MAX_VIDEO_SIZE', 100 * 1024 * 1024))
MAX_AUDIO_SIZE = int(os.getenv('MAX_AUDIO_SIZE', 50 * 1024 * 1024))

THUMBNAIL_SIZE = (int(os.getenv('THUMBNAIL_WIDTH', 300)), int(os.getenv('THUMBNAIL_HEIGHT', 300)))

MEDIA_TYPES = {
    'image': [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
        'image/bmp', 'image/tiff', 'image/x-icon'
    ],
    'video': [
        'video/mp4', 'video/webm', 'video/ogg', 'video/x-matroska',
        'video/quicktime', 'video/x-msvideo', 'video/x-flv', 'application/vnd.rn-realmedia'
    ],
    'audio': [
        'audio/mpeg', 'audio/ogg', 'audio/wav', 'audio/webm',
        'audio/aac', 'audio/flac', 'audio/x-ms-wma', 'audio/x-m4a'
    ],
}

MEDIA_EXTENSIONS = {
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.ico'],
    'video': ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv', '.wmv'],
    'audio': ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma']
}

URL_MEDIA_ATTRIBUTES = ['src', 'href', 'data-src', 'data-original', 'srcset', 'poster']

URL_KEYS = ['src', 'url', 'href', 'link', 'image', 'thumbnail', 'poster', 'source']
MEDIA_KEYS = ['image', 'photo', 'picture', 'img', 'video', 'audio', 'media', 'file']

SKIP_JSON_KEYS = ['script', 'function', 'options', 'settings', 'config']

FFMPEG_EXTRACT_FRAME_TIME = os.getenv('FFMPEG_EXTRACT_FRAME_TIME', '00:00:01')

SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5050))
WORKERS = int(os.getenv('WORKERS', 1))