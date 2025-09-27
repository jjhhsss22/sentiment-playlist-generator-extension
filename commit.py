# this file only needs to be executed once during initialisation of our database
# this will then create our tables on the local sql server

from website import app, db  # import your app and db
from dbmodels import User, Playlist

with app.app_context():
    db.create_all()  # creates all tables
    print("Tables committed to the database!")