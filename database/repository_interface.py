from database.dbmodels import User, Playlist, db
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(email, username, password):
    new_user = User(email=email,
                    username=username,
                    password=generate_password_hash(password, method='pbkdf2:sha256'))

    return new_user

def find_user_by_email(email):
    return User.query.filter_by(email=email).first()


def create_playlist(input_text, likely_emotion, desired_emotion, playlist_text, id):
    new_playlist = Playlist(prompt=input_text,
                            start_emotion=likely_emotion,
                            target_emotion=desired_emotion,
                            playlist=playlist_text,
                            user_id=id)

    return new_playlist

def save(new_record):
    db.session.add(new_record)
    db.session.commit()