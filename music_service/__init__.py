from flask import Flask, g, request
import logging

from log_logic.ms_logging_config import configure_logging


def create_ms():
    configure_logging()

    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.WARNING)

    app = Flask(__name__)

    from api_music_service_interface import ms_bp
    app.register_blueprint(ms_bp)

    @app.before_request
    def read_request_and_user_id():
        g.request_id = request.headers.get("request-id", "unknown")
        user_id = request.headers.get("user-id")
        g.user_id = int(user_id) if user_id is not None else None

    return app