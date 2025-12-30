from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()  # set up connection to SQLAlchemy commands


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # will automatically increment since it's the primary key
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    playlist = db.relationship('Playlist')  # one-to-many relationship with Playlist
    creation_date = db.Column(db.Date, default=date.today, nullable=False)  # get creation date using datetime module


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    start_emotion = db.Column(db.String(50), nullable=False)
    target_emotion = db.Column(db.String(50), nullable=False)
    playlist = db.Column(db.Text, nullable=False)  # playlist will just be one long string with songs separated by commas
    playlist_creation_date = db.Column(db.Date, default=date.today, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # foreign key from User
    request_id = db.Column(db.String(40), nullable=False, unique=True, index=True)  # idempotency key


