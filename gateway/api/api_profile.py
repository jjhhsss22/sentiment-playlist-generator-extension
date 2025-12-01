from flask import jsonify, request, Blueprint, current_app
import requests
from flask_jwt_extended import jwt_required, get_jwt_identity
from gateway.log_logic.log_util import log

api_profile_bp = Blueprint('api_profile', __name__)

DB_API_URL = "http://127.0.0.1:8003/playlist"
AUTH_API_URL = "http://127.0.0.1:8004/jwt/validate"

@api_profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def api_profile():
    if request.headers.get("X-Requested-With") != "ReactApp":
        log(30, "forbidden request received")
        return jsonify({"success": False,
                        "location": "/unknown",
                        "message": "Forbidden access"}), 403

    try:
        cookies = request.cookies
        auth_response = requests.get(AUTH_API_URL, cookies=cookies)

        auth_results = auth_response.json()

        if auth_response.status_code != 200:
            return auth_results, auth_response.status_code

        user_id = auth_results.get("user_id")

    except Exception as e:
        log(50, "auth server network error", error=str(e))
        return jsonify({
            "success": False,
            "message": "authentication server error. Please try again later."
        }), 500

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
            log(40, "db bad response")
            return jsonify({
                "success": False,
                "message": "Bad response from database server. Please try again later."
            }), 502

        if not response.ok:
            if results.get("forbidden", False):
                log(30, "db forbidden")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            db_message = results.get("message", "Error when retrieving playlists")
            log(40, "db error", status_code=response.status_code)
            return jsonify({"success": False, "message": db_message}), response.status_code

        playlists_data = results.get("playlists", [])
        return jsonify({"success": True, "playlists": playlists_data}), 200

    except Exception as e:
        log(50, "db network error", error=str(e))
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500