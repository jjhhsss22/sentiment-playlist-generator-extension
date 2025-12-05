from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from log_logic.auth_logging_config import configure_logging
import logging

def create_auth():
    configure_logging()

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)

    from log_logic.log_util import log

    app = Flask(__name__)

    # JWT configuration
    app.config["JWT_SECRET_KEY"] = "super-secret-key"
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_HTTPONLY"] = True
    app.config["JWT_COOKIE_SECURE"] = True   # True
    app.config["JWT_COOKIE_SAMESITE"] = "None"  # "None" for production

    jwt = JWTManager(app)

    from api.jwt_oauth import jwt_bp
    from api.user_auth import user_auth_bp
    app.register_blueprint(jwt_bp, url_prefix="/jwt")
    app.register_blueprint(user_auth_bp, url_prefix="/user")

    @jwt.unauthorized_loader
    def unauthorized_callback(err_msg):
        log(30, "unauthorised access", error=err_msg)

        return jsonify({
            "success": False,
            "jwt": "invalid",
            "location": "/login",
            "message": "Unauthorised access. Please log in again"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(err_msg):
        log(40, "invalid token", error=err_msg)

        return jsonify({
            "success": False,
            "jwt": "invalid",
            "location": "/login",
            "message": "Invalid session. Please log in again"
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        log(30, "expired token")

        return jsonify({
            "success": False,
            "jwt": "invalid",
            "location": "/login",
            "message": "Expired session. Please log in again"
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        log(40, "revoked token")

        return jsonify({
            "success": False,
            "jwt": "invalid",
            "location": "/login",
            "message": "Expired session. Please log in again"
        }), 401

    return app