import os
import logging

from flask import Blueprint, render_template, request, redirect, url_for, session, send_file

from app.services.cache import CacheManager

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():

    if 'session_id' not in session:
        cache_manager = CacheManager()
        session['session_id'] = cache_manager.create_session()

    return render_template('index.html')

@main_bp.route('/results')
def results():

    if 'session_id' not in session:
        return redirect(url_for('main.index'))

    url = request.args.get('url', '')
    if not url:
        return redirect(url_for('main.index'))

    cache_manager = CacheManager()
    session_id = session['session_id']

    if not cache_manager.session_exists(session_id):

        session['session_id'] = cache_manager.create_session()
        return redirect(url_for('main.index'))

    cache_manager.update_session_access_time(session_id)

    media_list = cache_manager.get_media_metadata(session_id)

    return render_template('results.html', url=url, media=media_list)

@main_bp.route('/media/<path:filename>')
def media_file(filename):

    if 'session_id' not in session:
        return redirect(url_for('main.index'))

    session_id = session['session_id']
    cache_manager = CacheManager()

    if not cache_manager.session_exists(session_id):
        return redirect(url_for('main.index'))

    file_path = os.path.join(cache_manager.get_session_path(session_id), filename)

    if not os.path.exists(file_path):
        logger.warning(f"Media file not found: {filename}")
        return "File not found", 404

    cache_manager.update_session_access_time(session_id)

    return send_file(file_path)

@main_bp.route('/thumbnail/<path:filename>')
def thumbnail(filename):

    if 'session_id' not in session:
        return redirect(url_for('main.index'))

    session_id = session['session_id']
    cache_manager = CacheManager()

    if not cache_manager.session_exists(session_id):
        return redirect(url_for('main.index'))

    file_path = os.path.join(cache_manager.get_session_path(session_id), 'thumbnails', filename)

    if not os.path.exists(file_path):
        logger.warning(f"Thumbnail not found: {filename}")
        return "Thumbnail not found", 404

    cache_manager.update_session_access_time(session_id)

    return send_file(file_path)

@main_bp.route('/clear-cache')
def clear_cache():

    if 'session_id' in session:
        cache_manager = CacheManager()
        cache_manager.clear_session(session['session_id'])
        session.pop('session_id', None)

    return redirect(url_for('main.index'))