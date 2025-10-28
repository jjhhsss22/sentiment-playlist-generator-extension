from flask import Flask, render_template, current_app
from flask_login import LoginManager
import pymysql
from database.dbmodels import db


def create_app():
    app = Flask(__name__)  # set up flask environment

    from api.api_profile import api_profile_bp
    from api.auth.api_auth_routes import api_auth_bp
    from api.api_home import api_home_bp
    from website import website_bp

    app.register_blueprint(api_profile_bp, url_prefix='/api')
    app.register_blueprint(api_auth_bp, url_prefix='/api')
    app.register_blueprint(api_home_bp, url_prefix='/api')
    app.register_blueprint(website_bp)  # register flask blueprints from api's and website

    pymysql.install_as_MySQLdb()  # initialise pymysql

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sqlsecretkey123@localhost/spge'  # mysql table directory
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # for better memory usage
    app.config['SECRET_KEY'] = 'sqlsecretkey123'  # our secret key

    db.init_app(app)  # binds the flask environment to our database

    login_manager = LoginManager()  # instance of LoginManager()
    login_manager.init_app(app)  # connect the manager to our flask app
    login_manager.login_view = "login"  # redirect to log in

    @login_manager.unauthorized_handler
    def unauthorized():
        current_app.logger.warning(f"Unauthorised access: 401")

        return render_template("unknown.html"), 401

    @app.errorhandler(404)
    def page_not_found(e):
        current_app.logger.warning(f"Resource not found: 404")
        return render_template("unknown.html"), 404


    from database.dbmodels import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, user_id)

    return app

