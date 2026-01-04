from flask import Flask, g, request
import uuid
from log_logic.gw_logging_config import configure_logging
import logging
import redis
from websocket.socket import socketio
from websocket.redis_subscriber import start_listener

def create_app():
    configure_logging() # logging setup

    log = logging.getLogger('werkzeug')  # to suppress HTTP logs from werkzeug
    log.setLevel(logging.WARNING)

    app = Flask(__name__)  # set up flask environment

    app.extensions["redis_cache"] = redis.Redis.from_url(
        "redis://localhost:6379/1",  # cache DB in redis instance
        decode_responses=True
    )

    socketio.init_app(app)
    start_listener()  # start redis subscriber thread (1 per gateway instance)

    from api.api_profile import api_profile_bp
    from api.api_home import api_home_bp
    from api.api_auth_routes import api_auth_bp
    from website import website_bp

    app.register_blueprint(api_profile_bp, url_prefix='/api')
    app.register_blueprint(api_home_bp, url_prefix='/api')
    app.register_blueprint(api_auth_bp, url_prefix='/api')
    app.register_blueprint(website_bp)  # register flask blueprints from api's and website

    @app.before_request
    def catch_direct_api_hits():
        if request.path.startswith("/api") and "text/html" in request.headers.get("Accept", ""):
            return app.send_static_file("index.html")

    @app.before_request
    def assign_request_id():
        # 1. If client sent one, reuse it
        incoming = request.headers.get("request-id")
        g.request_id = incoming or str(uuid.uuid4().hex)

    # @app.after_request
    # def add_request_and_user_id_header(response):
    #     response.headers["request_id"] = g.request_id
    #     response.headers["user_id"] = g.user_id
    #     return response

    return app

