from flask import Flask, current_app, request, jsonify
from flask_jwt_extended import JWTManager
from gw_logging_config import configure_logging
import logging

def create_app():
    configure_logging() # logging setup

    # log = logging.getLogger('werkzeug')  # to suppress HTTP logs from werkzeug
    # log.setLevel(logging.WARNING)

    app = Flask(__name__)  # set up flask environment

    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # secret JWT key for verification
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = True  # Use HTTPS
    app.config["JWT_COOKIE_SAMESITE"] = "None"
    app.config["JWT_COOKIE_HTTPONLY"] = True  # HttpOnly cookie
    jwt = JWTManager(app)
    jwt.init_app(app)

    from api.api_profile import api_profile_bp
    from api.auth.api_auth_routes import api_auth_bp
    from api.auth.api_validate_jwt import jwt_bp
    from api.api_home import api_home_bp
    from website import website_bp

    app.register_blueprint(api_profile_bp, url_prefix='/api')
    app.register_blueprint(api_auth_bp, url_prefix='/api')
    app.register_blueprint(api_home_bp, url_prefix='/api')
    app.register_blueprint(jwt_bp, url_prefix='/api')
    app.register_blueprint(website_bp)  # register flask blueprints from api's and website

    @jwt.unauthorized_loader
    def unauthorized_callback(err_msg):
        current_app.logger.warning(
            f"Unauthorized access | path={request.path} | ip={request.remote_addr} | msg={err_msg}"
        )  # current_app.logger now stored in stdout / stderr
        return jsonify({"success": False, "jwt": "invalid",
                        "location": "/login",
                        "message": "Unauthorised access. Please log in again"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(err_msg):
        current_app.logger.warning(
            f"Invalid token | path={request.path} | ip={request.remote_addr} | msg={err_msg}"
        )
        return jsonify({"success": False, "jwt": "invalid",
                        "location": "/login",
                        "message": "Invalid session. Please log in again"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        current_app.logger.info(
            f"Expired token | path={request.path} | ip={request.remote_addr}"
        )
        return jsonify({"success": False, "jwt": "invalid",
                        "location": "/login",
                        "message": "Expired session. Please log in again"}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        current_app.logger.warning(
            f"Revoked token | path={request.path} | ip={request.remote_addr}"
        )
        return jsonify({"success": False,
                        "jwt": "invalid",
                        "location": "/login",
                        "message": "Expired session. Please log in again"}), 401

    @app.before_request
    def catch_direct_api_hits():
        if request.path.startswith("/api") and "text/html" in request.headers.get("Accept", ""):
            return app.send_static_file("index.html")

    return app

