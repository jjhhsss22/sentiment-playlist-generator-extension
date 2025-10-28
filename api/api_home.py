from flask import request, jsonify, Blueprint, current_app, render_template
from flask_login import login_required, current_user

from tensorflow.errors import InvalidArgumentError

from database.dbmodels import db, Playlist
from AI.deployment.service_interface import run_prediction_pipeline
from music.music_module import Songs, get_quadrant_object
import music.music_object_database


api_home_bp = Blueprint('api_home', __name__)

@api_home_bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return render_template("unknown.html"), 403

    data = request.get_json()

    input_text = data.get("text", "").strip()
    desired_emotion = data.get("emotion", None)

    if not input_text or not desired_emotion:
        return jsonify({
            "success": False,
            "message": "Please fill out all forms for a playlist to be generated"
        })

    try:
        try:
            results = run_prediction_pipeline(input_text, desired_emotion)  # 2D array with probabilities of emotions
        except InvalidArgumentError:
            return jsonify({
                "success": False,
                "message": "Please submit text in full sentences"
            })

        predictions_list = results["predictions_list"]
        predicted_emotions = results["predicted_emotions"]
        likely_emotion = results["likely_emotion"]
        starting_coord = results["starting_coord"]
        target_coord = results["target_coord"]
        others_probability = results["others_probability"]

        start_object = get_quadrant_object("start", starting_coord)
        target_object = get_quadrant_object("target", target_coord)

        playlist = start_object.find_playlist(target_object)

        if len(playlist) <= 2:
            return jsonify({
                "success": False,
                "message": "No available songs with the provided emotions. You are already near your desired emotion!"
            })

        Songs.delete_object(start_object)
        Songs.delete_object(target_object)  # delete the temporary objects

        songs_playlist = Songs.get_named_playlist(playlist)  # convert the object list to named list
        songs_playlist_text = ', '.join(songs_playlist)  # convert the list into string

        new_playlist = Playlist(prompt=input_text,
                                start_emotion=likely_emotion,
                                target_emotion=desired_emotion,
                                playlist=songs_playlist_text,
                                user_id=current_user.id)

        db.session.add(new_playlist)
        db.session.commit()  # add to the database

        return jsonify({
            "success": True,
            "message": "Playlist generated successfully!",
            "input_text": input_text,
            "desired_emotion": desired_emotion,
            "songs_playlist": songs_playlist,
            "predicted_emotions": predicted_emotions,
            "predictions_list": predictions_list,
            "others_prediction": others_probability
        })  # pass our variables to the React frontend as JSON

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "message": "Error when generating playlist. Please try again."
        })