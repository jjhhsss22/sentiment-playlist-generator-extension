from flask import jsonify, request, Blueprint, g
import requests

from gateway.log_logic.log_util import log

api_profile_bp = Blueprint('api_profile', __name__)

DB_API_URL = "http://127.0.0.1:8003/playlist"
AUTH_API_URL = "http://127.0.0.1:8004/jwt/verify"

@api_profile_bp.route('/profile', methods=['GET'])
def api_profile():
    if request.headers.get("X-Requested-With") != "ReactApp":
        log(30, "forbidden request received")
        return jsonify({"success": False,
                        "location": "/unknown",
                        "message": "Forbidden access"}), 403

    try:
        headers = {"request-id": g.request_id,
                   "API-Requested-With": "Home Gateway"
                   }

        cookies = {
            "access_token_cookie": request.cookies.get("access_token_cookie")
        }

        auth_response = requests.get(
            AUTH_API_URL,
            headers=headers,
            cookies=cookies,
            timeout=5
        )

        try:
            auth_results = auth_response.json()
        except Exception as e:
            log(40, "auth bad response", error=e)
            return jsonify({
                "success": False,
                "message": "Bad response from authentication server. Please try again later."
            }), 502

        if auth_response.status_code != 200:
            return jsonify(auth_results), auth_response.status_code

        user_id = auth_results.get("user_id")
        g.user_id = user_id

    except Exception as e:
        log(50, "auth server network error", error=str(e))
        return jsonify({
            "success": False,
            "message": "Authentication server error. Please try again later."
        }), 500

    try:
        headers = {"request-id": g.request_id,
                   "user-id": str(g.user_id),
                   "API-Requested-With": "Home Gateway"
                   }

        response = requests.post(
            DB_API_URL,
            headers=headers
        )

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