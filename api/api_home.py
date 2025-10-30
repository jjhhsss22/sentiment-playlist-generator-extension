from flask import request, jsonify, Blueprint, current_app, render_template
import requests
from flask_login import login_required, current_user

from database.repository_interface import create_playlist, save

api_home_bp = Blueprint('api_home', __name__)

AI_SERVER_URL = "http://localhost:8001/predict"
MUSIC_SERER_URL = "http://localhost:8002/playlist"

@api_home_bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return render_template("unknown.html")

    data = request.get_json()

    input_text = data.get("text", "").strip()
    desired_emotion = data.get("emotion", None)

    try:
        ai_response = requests.post(AI_SERVER_URL, json={
            "API-Requested-With": "Home Gateway",
            "text": input_text,
            "emotion": desired_emotion
        }, timeout=10)

        if ai_response.status_code != 200:
            return jsonify({"success": False, "message": "failed to connect to ai_service server "})

        ai_results = ai_response.json()

        print(ai_results)

        if ai_results.get("forbidden", False):
            current_app.logger.warning(f"Forbidden access to ai server: 403")
            return render_template('unknown.html')

        if not ai_results.get("success"):
            return jsonify(ai_results)

        ai_data = ai_results["result"]
        predictions_list = ai_data["predictions_list"]
        predicted_emotions = ai_data["predicted_emotions"]
        likely_emotion = ai_data["likely_emotion"]
        starting_coord = ai_data["starting_coord"]
        target_coord = ai_data["target_coord"]
        others_probability = ai_data["others_probability"]

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "message": "Error when predicting emotion. Please try again later."
        })

    try:
        music_response = requests.post(MUSIC_SERER_URL, json={
            "API-Requested-With": "Home Gateway",
            "starting_coord": starting_coord,
            "target_coord": target_coord,
        })

        if music_response.status_code != 200:
            return jsonify({"success": False, "message": "failed to connect to music server "})

        music_results = music_response.json()

        if music_results.get("forbidden", False):
            current_app.logger.warning(f"Forbidden access to ai server: 403")
            return render_template('unknown.html')

        music_data = music_results["result"]
        playlist_list = music_data["list"]
        playlist_text = music_data["text"]

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
            "message": "Error when generating playlist. Please try again later."
        })