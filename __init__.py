from flask import Flask, render_template, current_app
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__)  # set up flask environment

    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # secret JWT key for verification
    jwt = JWTManager(app)
    jwt.init_app(app)

    from api.api_profile import api_profile_bp
    from api.auth.api_auth_routes import api_auth_bp
    from api.api_home import api_home_bp
    from website import website_bp

    app.register_blueprint(api_profile_bp, url_prefix='/api')
    app.register_blueprint(api_auth_bp, url_prefix='/api')
    app.register_blueprint(api_home_bp, url_prefix='/api')
    app.register_blueprint(website_bp)  # register flask blueprints from api's and website

    @jwt.unauthorized_loader
    def unauthorized_callback(err_msg):
        current_app.logger.warning(f"Unauthorised access: 401 ({err_msg})")
        return render_template("unknown.html"), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(err_msg):
        current_app.logger.warning(f"Invalid token: {err_msg}")
        return render_template("login.html"), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        current_app.logger.warning("Token expired")
        return render_template("login.html"), 401

    @app.errorhandler(404)
    def page_not_found(e):
        current_app.logger.warning("Resource not found: 404")
        return render_template("unknown.html"), 404


    return app

