import os
import asyncio
import logging
import traceback

from typing import Dict, Any, Tuple, Optional, List
from flask import Blueprint, request, jsonify, session

from app.services.crawler import Crawler
from app.services.media import MediaDownloader
from app.services.cache import CacheManager
from app.utils.url import is_valid_url, normalize_url
from app.config import MAX_CRAWL_DEPTH

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_bp.route('/crawl', methods=['POST'])
def crawl():
    params = _extract_crawl_params()
    if 'error' in params:
        return jsonify({'error': params['error']}), 400

    url = params['url']
    depth = params['depth']

    cache_manager = CacheManager()
    session_id = _setup_cache_session(cache_manager)

    try:
        return _perform_crawl(url, depth, session_id, cache_manager)
    except Exception as e:
        error_message = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"Error crawling {url}: {error_message}\n{stack_trace}")
        return jsonify({
            'error': error_message,
            'success': False,
            'session_id': session_id,
            'url': url
        }), 500

def _extract_crawl_params() -> Dict[str, Any]:
    url = request.json.get('url', '')
    depth = request.json.get('depth', MAX_CRAWL_DEPTH)

    if not is_valid_url(url):
        return {'error': 'Invalid URL'}

    return {
        'url': normalize_url(url),
        'depth': depth
    }

def _setup_cache_session(cache_manager: CacheManager) -> str:
    if 'session_id' in session and cache_manager.session_exists(session['session_id']):
        logger.info(f"Clearing previous session: {session['session_id']}")
        cache_manager.clear_session(session['session_id'])

    session_id = cache_manager.create_session()
    session['session_id'] = session_id
    logger.info(f"Created new cache session: {session_id}")

    return session_id

def _perform_crawl(url: str, depth: int, session_id: str, cache_manager: CacheManager) -> Tuple[Dict[str, Any], int]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:

        crawler = Crawler(session_id=session_id)
        stats, media_urls = loop.run_until_complete(crawler.crawl(url, depth))

        if media_urls:
            logger.info(f"Found {len(media_urls)} media URLs: {', '.join(media_urls[:5])}")
        else:
            logger.warning(f"No media URLs found when crawling {url}")
            return jsonify({
                'success': True,
                'media_count': 0,
                'stats': stats.to_dict(),
                'warning': 'No media files found on the page'
            }), 200

        try:
            downloader = MediaDownloader(session_id=session_id)
            media_list = loop.run_until_complete(downloader.download_media(media_urls, url))
        except Exception as e:
            logger.error(f"Error downloading media: {e}")

            return jsonify({
                'success': False,
                'error': f"Found {len(media_urls)} media URLs but failed to download: {str(e)}",
                'stats': stats.to_dict(),
                'session_id': session_id
            }), 200

        cache_manager.update_session_access_time(session_id)

        session_stats = cache_manager.get_session_stats(session_id)

        return jsonify({
            'success': True,
            'media_count': len(media_list),
            'stats': stats.to_dict(),
            'session_id': session_id,
            'cache_info': _build_cache_info(cache_manager, session_id, media_list, session_stats)
        }), 200
    finally:

        try:
            loop.close()
        except Exception as e:
            logger.warning(f"Error closing event loop: {e}")

def _build_cache_info(
    cache_manager: CacheManager,
    session_id: str,
    media_list: List[Any],
    session_stats: Dict[str, Any]
) -> Dict[str, Any]:

    session_path = cache_manager.get_session_path(session_id)
    return {
        'path': str(session_path),
        'media_count': len(media_list),
        'disk_usage': session_stats.get('disk_usage', 0)
    }

@api_bp.route('/media', methods=['GET'])
def get_media():

    session_info = _check_active_session()
    if 'error' in session_info:
        return jsonify({'error': session_info['error']}), session_info['status_code']

    session_id = session_info['session_id']
    cache_manager = session_info['cache_manager']

    cache_manager.update_session_access_time(session_id)

    media_list = cache_manager.get_media_metadata(session_id)

    session_stats = cache_manager.get_session_stats(session_id)

    session_path = cache_manager.get_session_path(session_id)

    return jsonify({
        'media': media_list,
        'count': len(media_list),
        'session_id': session_id,
        'cache_info': {
            'path': str(session_path),
            'media_count': len(media_list),
            'disk_usage': session_stats.get('disk_usage', 0),
            'media_types': session_stats.get('media_types', {})
        }
    })

@api_bp.route('/media/<media_id>', methods=['GET'])
def get_media_item(media_id):

    session_info = _check_active_session()
    if 'error' in session_info:
        return jsonify({'error': session_info['error']}), session_info['status_code']

    session_id = session_info['session_id']
    cache_manager = session_info['cache_manager']

    cache_manager.update_session_access_time(session_id)

    media = cache_manager.get_media_by_id(session_id, media_id)

    if media:
        return jsonify(media)

    media = _find_media_by_filename(cache_manager, session_id, media_id)

    if media:
        return jsonify(media)

    return jsonify({'error': 'Media not found'}), 404

def _find_media_by_filename(cache_manager: CacheManager, session_id: str, filename: str) -> Optional[Dict[str, Any]]:

    media_list = cache_manager.get_media_metadata(session_id)
    for media in media_list:
        if os.path.basename(media.get('file_path', '')) == filename:
            return media
    return None

def _check_active_session() -> Dict[str, Any]:

    if 'session_id' not in session:
        return {
            'error': 'No active session',
            'status_code': 400
        }

    session_id = session['session_id']
    cache_manager = CacheManager()

    if not cache_manager.session_exists(session_id):
        return {
            'error': 'Session not found',
            'status_code': 404
        }

    return {
        'session_id': session_id,
        'cache_manager': cache_manager
    }

@api_bp.route('/status', methods=['GET'])
def get_status():

    if 'session_id' not in session:
        return jsonify({'status': 'no_session'})

    session_id = session['session_id']
    cache_manager = CacheManager()

    if not cache_manager.session_exists(session_id):
        session.pop('session_id', None)
        return jsonify({'status': 'no_session'})

    cache_manager.update_session_access_time(session_id)

    session_stats = cache_manager.get_session_stats(session_id)

    session_path = cache_manager.get_session_path(session_id)

    return jsonify({
        'status': 'active',
        'session_id': session_id,
        'media_count': session_stats.get('media_count', 0),
        'cache_info': {
            'path': str(session_path),
            'disk_usage': session_stats.get('disk_usage', 0),
            'created_at': session_stats.get('created_at'),
            'last_accessed': session_stats.get('last_accessed'),
            'media_types': session_stats.get('media_types', {})
        }
    })

@api_bp.route('/clear-cache', methods=['POST'])
def clear_cache():

    if 'session_id' not in session:
        return jsonify({'status': 'no_session'})

    session_id = session['session_id']
    cache_manager = CacheManager()

    session_stats = {}
    if cache_manager.session_exists(session_id):
        session_stats = cache_manager.get_session_stats(session_id)
        cache_manager.clear_session(session_id)
        logger.info(f"Manually cleared cache session: {session_id}")

    new_session_id = cache_manager.create_session()
    session['session_id'] = new_session_id

    return jsonify({
        'success': True,
        'message': 'Cache cleared',
        'previous_session_id': session_id,
        'new_session_id': new_session_id
    })

@api_bp.route('/cache-info', methods=['GET'])
def get_cache_info():

    cache_manager = CacheManager()

    total_size = cache_manager.get_cache_size()

    current_session = _get_current_session_info(cache_manager)

    base_cache_dir = str(cache_manager.path_manager.base_cache_dir)

    return jsonify({
        'cache_dir': base_cache_dir,
        'total_size': total_size,
        'current_session': current_session
    })

def _get_current_session_info(cache_manager: CacheManager) -> Optional[Dict[str, Any]]:

    if 'session_id' not in session or not cache_manager.session_exists(session['session_id']):
        return None

    session_id = session['session_id']
    session_stats = cache_manager.get_session_stats(session_id)

    session_path = cache_manager.get_session_path(session_id)

    return {
        'session_id': session_id,
        'path': str(session_path),
        'media_count': session_stats.get('media_count', 0),
        'disk_usage': session_stats.get('disk_usage', 0),
        'media_types': session_stats.get('media_types', {})
    }