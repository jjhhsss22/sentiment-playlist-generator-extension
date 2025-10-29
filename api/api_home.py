from flask import request, jsonify, Blueprint, current_app, render_template
from flask_login import login_required, current_user

from tensorflow.errors import InvalidArgumentError

from database.repository_interface import create_playlist, save
from AI.deployment.ai_service_interface import run_prediction_pipeline
from music.music_service_interface import generate_playlist_pipeline
import music.music_logic.music_object_database

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

    try:
        try:
            ai_results = run_prediction_pipeline(input_text, desired_emotion)  # 2D array with probabilities of emotions
        except InvalidArgumentError:
            return jsonify({
                "success": False,
                "message": "Please submit text in full sentences"
            })

        predictions_list = ai_results["predictions_list"]
        predicted_emotions = ai_results["predicted_emotions"]
        likely_emotion = ai_results["likely_emotion"]
        starting_coord = ai_results["starting_coord"]
        target_coord = ai_results["target_coord"]
        others_probability = ai_results["others_probability"]

        playlist_results = generate_playlist_pipeline(starting_coord, target_coord)

        playlist_list = playlist_results["playlist_list"]
        playlist_text = playlist_results["playlist_text"]

        if len(playlist_list) <= 2:
            return jsonify({
                "success": False,
                "message": "No available songs with the provided emotions. You are already near your desired emotion!"
            })

        new_playlist = create_playlist(input_text,
                                       likely_emotion,
                                       desired_emotion,
                                       playlist_text,
                                       current_user.id)
        save(new_playlist)  # call to repository interface

        return jsonify({
            "success": True,
            "message": "Playlist generated successfully!",
            "input_text": input_text,
            "desired_emotion": desired_emotion,
            "songs_playlist": playlist_list,
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