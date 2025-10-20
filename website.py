from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, LoginManager, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from tensorflow.errors import InvalidArgumentError

from dbmodels import db, User, Playlist
from Userlogin import is_valid_username, is_valid_password
from AIModel import predict, get_predicted_emotion, get_starting_coord, get_target_coord, to_list
from Music import Songs, get_quadrant_object

app = Flask(__name__)  # set up flask environment

pymysql.install_as_MySQLdb()  # initialise pymysql


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sqlsecretkey123@localhost/spge'  # mysql table directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # for better memory usage
app.config['SECRET_KEY'] = 'sqlsecretkey123'  # our secret key

db.init_app(app)  # binds the flask environment to our database

login_manager = LoginManager()  # instance of LoginManager()
login_manager.init_app(app)  # connect the manager to our flask app
login_manager.login_view = "login"  # redirect to log in


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)



@app.route('/', methods=['GET', 'POST'])
@login_required  # requires the user to be authenticated
def home():
    if request.method == 'POST':
        data = request.get_json()

        input_text = data.get("text", "").strip()
        desired_emotion = data.get("emotion", None)

        emotions =['Anger', 'Boredom', 'Empty',
               'Enthusiasm', 'Fun', 'Happiness',
               'Hate', 'Love', 'Neutral',
               'Relief', 'Sadness', 'Surprise', 'Worry']

        if not input_text or not desired_emotion:
            return jsonify({
                "success": False,
                "message": "Please fill out all forms for a playlist to be generated"
            })

        try:
            try:
                predictions = predict(input_text)  # 2D array with probabilities of emotions
            except InvalidArgumentError:
                return jsonify({
                    "success": False,
                    "message": "Please submit text in full sentences"
                })

            predicted_emotion = get_predicted_emotion(predictions)  # most likely emotion

            starting_coord = get_starting_coord(predictions)  # starting coord algorithm applied
            target_coord = get_target_coord(desired_emotion)  # target coord found using the checkbox input

            start_object = get_quadrant_object("start", starting_coord)
            target_object = get_quadrant_object("target", target_coord)

            playlist = start_object.find_playlist(target_object)

            if len(playlist) <= 2:
                return jsonify({
                    "success": False,
                    "message": "No available songs with the provided emotions. You are already at your desired emotion!"
                })

            predictions_list = to_list(predictions[0])  # convert the 2D array to a list
            i = 0
            total_prediction_sum = 0

            while i < len(predictions_list):
                if predictions_list[i] < 0.05:  # filter out insignificant emotions
                    del predictions_list[i]

                    del emotions[i]
                else:
                    total_prediction_sum += predictions_list[i]  # also find the total of the significant emotions
                    i += 1                                       # for the OTHERS bar in home.html

            Songs.delete_object(start_object)
            Songs.delete_object(target_object)  # delete the temporary objects

            songs_playlist = Songs.get_named_playlist(playlist)  # convert the object list to named list
            songs_playlist_text = ', '.join(songs_playlist)  # convert the list into string

            new_playlist = Playlist(prompt=input_text,
                                    start_emotion=predicted_emotion,
                                    target_emotion=desired_emotion,
                                    playlist=songs_playlist_text,
                                    user_id=current_user.id)

            db.session.add(new_playlist)
            db.session.commit()  # add to the database

            return jsonify({
                "success": True,
                "message": "Playlist generated successfully!",
                "data": {
                    "input_text": input_text,
                    "predicted_emotion": predicted_emotion,
                    "desired_emotion": desired_emotion,
                    "songs_playlist": songs_playlist,
                    "emotions": emotions,
                    "predictions": predictions_list,
                    "total_prediction_sum": total_prediction_sum
                }  # pass our variables to the React frontend as JSON
            })

        except Exception as e:
            app.logger.error(f"Error: {e}")
            return jsonify({
                "success": False,
                "message": "Error when generating playlist. Please try again."
            })

    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()

        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:  # verification
            return jsonify({"success": False, "message": "Invalid email"})
        elif not user.username == username:
            return jsonify({"success": False, "message": "Invalid username"})
        elif not check_password_hash(user.password, password):
            return jsonify({"success": False, "message": "Invalid password"})
        else:
            login_user(user, remember=True)
            return jsonify({"success": True, "message": f"Welcome {username}, you are logged in"})

    return render_template("login.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':  # when there has been a user input
        data = request.get_json()  # data from the form

        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirmPassword')  # id from the HTML file

        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "Email already linked to an account."})

        elif not is_valid_username(username):
            return jsonify({"success": False, "message": "Invalid username — cannot contain spaces."})

        elif not is_valid_password(password, confirm_password):
            return jsonify({"success": False, "message": "Invalid password or mismatch."})

        else:
            new_user = User(email=email,
                            username=username,
                            password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()  # add the values to the database a new user

            login_user(new_user, remember=True)  # user session created with LoginManager

            return jsonify({"success": True,
                            "message": f"{username}, your account has been created!"})

    return render_template("signup.html")  # if no form is submitted, render the HTML for the signup page


@app.route('/profile')
@login_required
def profile():

    playlists = Playlist.query.filter_by(user_id=current_user.id).all()  # query the database for all playlists
                                                                         # created by the current user and store it in a list
    playlist_data = []

    for playlist in playlists:
        playlist_data.append({
            'prompt': playlist.prompt,
            'start_emotion': playlist.start_emotion,
            'target_emotion': playlist.target_emotion,
            'playlist': playlist.playlist.split(','),  # convert the comma-separated string to a list
            'creation_date': playlist.playlist_creation_date
        })  # for each playlist, create a different list with all its information in a dictionary

    playlist_data.reverse()  # reverse the list so that the most recent playlists are at the top of the page

    return render_template("profile.html", playlists=playlist_data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("login.html")

    # return jsonify({"success": True, "message": "you have been logged out."})



# Run the app
if __name__ == "__main__":
    app.run(debug=True)
