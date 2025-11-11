from flask import request, jsonify, Blueprint, current_app, render_template
import requests
import time
from flask_jwt_extended import jwt_required, get_jwt_identity

api_home_bp = Blueprint('api_home', __name__)

AI_SERVER_URL = "http://127.0.0.1:8001"
MUSIC_SERER_URL = "http://127.0.0.1:8002/playlist"
DB_API_URL = "http://127.0.0.1:8003/new-playlist"

@api_home_bp.route('/home', methods=['GET', 'POST'])
@jwt_required()
def home():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return render_template("unknown.html")

    user_id = int(get_jwt_identity())

    data = request.get_json()

    input_text = data.get("text", "").strip()
    desired_emotion = data.get("emotion", None)

    try:
        ai_response = requests.post(f"{AI_SERVER_URL}/predict", json={
            "API-Requested-With": "Home Gateway",
            # no need for IP whitelisting or internal secret key
            # because api servers only accessible from this gateway server
            "text": input_text,
            "emotion": desired_emotion
        })

        if ai_response.status_code != 200:
            current_app.logger.error(f"Error status code: {ai_response.status_code}")
            return jsonify({"success": False, "message": "failed to connect to ai server "})

        ai_results = ai_response.json()

        if ai_results.get("forbidden", False):
            current_app.logger.warning(f"Forbidden access to ai server: 403")
            return render_template('unknown.html')

        if not ai_results.get("success"):
            return jsonify(ai_results)

        task_id = ai_results.get("task_id")
        print(task_id)

        for _ in range(10):  # retry up to 10 times

            '''
            simple setup for now as AI most likely won't take more than 5 seconds
            but should setup another celery task form this gateway server to constantly poll the AI task until it's done
            '''

            time.sleep(0.5)
            status_resp = requests.get(f"{AI_SERVER_URL}/task/{task_id}")
            status_data = status_resp.json()
            print(status_data)

            if status_data.get("status") == "done":
                ai_data = status_data["result"]

                print(ai_data)

                predictions_list = ai_data["predictions_list"]
                predicted_emotions = ai_data["predicted_emotions"]
                likely_emotion = ai_data["likely_emotion"]
                starting_coord = ai_data["starting_coord"]
                target_coord = ai_data["target_coord"]
                others_probability = ai_data["others_probability"]

                break
        else:
            return jsonify({
                "success": False,
                "message": "Error when predicting emotion. Please try again later."
            })

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "message": "AI server error. Please try again later."
        })

    try:
        music_response = requests.post(MUSIC_SERER_URL, json={
            "API-Requested-With": "Home Gateway",
            "starting_coord": starting_coord,
            "target_coord": target_coord,
        })

        if music_response.status_code != 200:
            current_app.logger.error(f"Error status code: {music_response.status_code}")
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

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "message": "Error when generating playlist. Please try again later."
            })

    try:
        db_response = requests.post(
            DB_API_URL,
            json={
                "API-Requested-With": "Home Gateway",
                "text": input_text,
                "likely_emotion": likely_emotion,
                "desired_emotion": desired_emotion,
                "playlist_text": playlist_text,
                "user_id": user_id
            })

        if db_response.status_code != 201:
            current_app.logger.error(f"Error status code: {db_response.status_code}")
            return jsonify({"success": False, "message": "failed to connect to db server "}), 500

        db_results = db_response.json()

        if not db_results.get("success"):
            current_app.logger.error("Playlist creation failed in db server")
            return jsonify(db_results), 400

        return jsonify({
            "success": True,
            "message": "Playlist generated successfully!",
            "desired_emotion": desired_emotion,
            "songs_playlist": playlist_list,
            "predicted_emotions": predicted_emotions,
            "predictions_list": predictions_list,
            "others_prediction": others_probability
        })

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({
            "success": False,
            "message": "Error when saving playlist. Please try again later."
        })
