from db_service.db_structure.dbmodels import User, Playlist, db
from werkzeug.security import generate_password_hash


def create_user(email, username, password):
    new_user = User(email=email,
                    username=username,
                    password=generate_password_hash(password, method='pbkdf2:sha256'))

    return new_user

def get_user_info(email):
    user = User.query.filter_by(email=email).first()

    return user


def get_playlists(user_id):
    playlists = Playlist.query.filter_by(user_id=user_id).all()  # query the db_service for all playlists
                                                                 # created by the current user and store it in a list
    playlist_data = []

    for playlist in playlists:
        playlist_data.append({
            "prompt": playlist.prompt,
            "start_emotion": playlist.start_emotion,
            "target_emotion": playlist.target_emotion,
            "playlist": playlist.playlist.split(','),  # convert the comma-separated string to a list
            "creation_date": playlist.playlist_creation_date.strftime("%Y-%m-%d")
        })  # for each playlist, create a different list with all its information in a dictionary

    playlist_data.reverse()  # reverse the list so that the most recent playlists are at the top of the page

    return playlist_data


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