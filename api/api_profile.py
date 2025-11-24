from flask import jsonify, request, Blueprint, current_app
import requests
from flask_jwt_extended import jwt_required, get_jwt_identity

api_profile_bp = Blueprint('api_profile', __name__)

DB_API_URL = "http://127.0.0.1:8003/playlist"

@api_profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def api_profile():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")
        return jsonify({"success": False,
                        "location": "/unknown",
                        "message": "Forbidden access"}), 403

    user_id = int(get_jwt_identity())

    try:
        response = requests.post(
            DB_API_URL,
            json={
                "API-Requested-With": "Home Gateway",
                "user_id": user_id
            })

        try:
            results = response.json()
        except Exception:
            current_app.logger.error("bad response from db server")
            return jsonify({
                "success": False,
                "message": "Bad response from database server. Please try again later."
            }), 502

        if not response.ok:
            if results.get("forbidden", False):
                current_app.logger.warning(f"Forbidden access to db server: 403")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            db_message = results.get("message", "Error when retrieving playlists")
            current_app.logger.error(f"Error status code: {response.status_code}")
            return jsonify({"success": False, "message": db_message}), response.status_code

        playlists_data = results.get("playlists", [])
        return jsonify({"success": True, "playlists": playlists_data}), 200

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500