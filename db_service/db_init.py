from flask import Flask
from db_service.db_structure.dbmodels import db
import pymysql

pymysql.install_as_MySQLdb()

def create_db():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sqlsecretkey123@localhost/spge'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sqlsecretkey123'

    db.init_app(app)

    return app