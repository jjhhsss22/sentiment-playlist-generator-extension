from flask import Flask, g, request
import pymysql
import logging

from db_service.db_structure.dbmodels import db
from log_logic.db_logging_config import configure_logging

pymysql.install_as_MySQLdb()

def create_db():
    configure_logging()

    wz_log = logging.getLogger('werkzeug')
    wz_log.setLevel(logging.WARNING)

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sqlsecretkey123@localhost/spge'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sqlsecretkey123'

    db.init_app(app)

    from api_repository_interface import db_bp
    app.register_blueprint(db_bp)

    @app.before_request
    def read_request_and_user_id():
        g.request_id = request.headers.get("request-id", "unknown")
        user_id = request.headers.get("user-id")
        g.user_id = int(user_id) if user_id is not None else None

    return app