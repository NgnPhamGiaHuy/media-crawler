import logging
import signal
import sys
from datetime import datetime
from pathlib import Path
from functools import partial
from flask import Flask, render_template

from app.routes import register_blueprints
from app.services.cache import CacheManager
from app.config.settings import (
    DEBUG, SECRET_KEY, CACHE_DIR, HOST, PORT
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():

    app = Flask(__name__,
        template_folder='app/templates',
        static_folder='app/static'
    )

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG
    app.config['JSON_SORT_KEYS'] = False

    register_blueprints(app)

    @app.context_processor
    def inject_globals():

        return {
            'now': datetime.now()
        }

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', error_code=500, message="Server error"), 500

    return app

def cleanup_cache():

    try:
        logger.info("Cleaning up all cache sessions on shutdown...")
        cache_manager = CacheManager(CACHE_DIR)
        sessions_cleared = cache_manager.clean_expired_sessions(expiry_time=0)
        logger.info(f"Cleared {sessions_cleared} cache sessions")
    except Exception as e:
        logger.error(f"Error cleaning up cache sessions: {e}")

def signal_handler(sig, frame):

    logger.info(f"Received signal {sig}, cleaning up...")
    cleanup_cache()
    sys.exit(0)

def clean_expired_on_startup():

    cache_manager = CacheManager(CACHE_DIR)
    cleaned = cache_manager.clean_expired_sessions()
    logger.info(f"Cleaned {cleaned} expired cache sessions on startup")

if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    clean_expired_on_startup()

    app = create_app()
    app.run(host=HOST, port=PORT)