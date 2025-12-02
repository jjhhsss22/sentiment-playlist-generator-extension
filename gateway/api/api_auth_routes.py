from flask import (
    request,
    jsonify,
    Blueprint,
    current_app)
import requests

from gateway.log_logic.log_util import log

api_auth_bp = Blueprint('auth', __name__)

DB_API_URL = "http://127.0.0.1:8003"
AUTH_API_URL = "http://127.0.0.1:8004"

@api_auth_bp.route('/signup', methods=['POST'])
def signup():
    if request.headers.get("X-Requested-With") != "ReactApp":
        log(30, "forbidden request received")
        return jsonify({"success": False,
                        "location": "/unknown",
                        "message": "Forbidden access"}), 403

    try:
        data = request.get_json()  # data from the form
    except Exception:
        log(40, "front bad response")
        return jsonify({"success": False, "message": "Bad response. Please try again"}), 502

    try:
        validate_response = requests.post(
            f"{AUTH_API_URL}/user/validate",
            headers={
                "API-Requested-With": "Home Gateway"
            },
            json=data
        )

        try:
            validate_result = validate_response.json()
        except Exception:
            log(40, "auth bad response")
            return jsonify({"success": False, "message": "Authentication server error"}), 502

        if not validate_response.ok:
            if validate_result.get("forbidden", False):
                log(30, "authentication forbidden")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            validate_message = validate_result.get("message", "Failed to access authentication server")
            log(40, "auth error", status_code=validate_response.status_code)
            return jsonify({"success": False, "message": validate_message}), validate_response.status_code

        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirmPassword')

        user_id =validate_result.get("user_id")

    except Exception as e:
        log(50, "db network error", error=str(e))
        return jsonify({"success": False, "message": "Authentication server error. Please try again later."}), 500

    try:

        assign_response = requests.post(
            f"{AUTH_API_URL}/jwt/assign",
            headers={
                "API-Requested-With": "Home Gateway"
            },
            json={
                "user_id": user_id,
                "username": username
            }
        )

        try:
            assign_result = assign_response.json()
        except Exception:
            log(40, "auth bad response")
            return jsonify({"success": False, "message": "Auth service error"}), 502

        if not assign_response.ok:
            if assign_result.get("forbidden", False):
                log(30, "auth forbidden")
                return jsonify({
                    "success": False,
                    "location": "/unknown",
                    "message": "Forbidden access"
                }), 403

            assign_message = assign_result.get("message", "Failed to assign JWT")
            log(40, "auth error", status_code=assign_response.status_code)
            return jsonify({"success": False, "message": assign_message}), assign_response.status_code

        resp = jsonify({
            "success": True,
            "message": f"Hello {username}, your account has been created!",
        })

        # Forward cookies set by Auth:
        for cookie in assign_response.cookies:
            resp.set_cookie(
                cookie.name,
                cookie.value,
                **cookie.__dict__.get('_rest', {})  # preserve cookie flags
            )

        return resp, 201

    except Exception as e:
        log(40, "auth jwt assignment error", error=str(e))
        return jsonify({
            "success": False,
            "message": "Auth service error. Please try again later."
        }), 403


@api_auth_bp.route('/login', methods=['POST'])
def login():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return jsonify({"success": False,
                        "location": "/unknown",
                        "message": "Forbidden access"}), 403

    try:
        data = request.get_json()
    except Exception:
        log(40, "front bad response")
        return jsonify({"success": False, "message": "Bad response. Please try again"}), 502

    try:
        verify_response = requests.post(
            f"{AUTH_API_URL}/user/verify",
            headers={
                "API-Requested-With": "Home Gateway"
            },
            json=data
        )

        try:
            verify_result = verify_response.json()
        except Exception:
            log(40, "auth bad response")
            return jsonify({"success": False, "message": "Authentication server error"}), 502

        if not verify_response.ok:
            if verify_result.get("forbidden", False):
                log(30, "auth forbidden")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            verify_message = verify_result.get("message", "Failed to access authentication server")
            log(40, "auth error", status_code=verify_response.status_code)
            return jsonify({"success": False, "message": verify_message}), verify_response.status_code

        user_id = verify_result.get("user_id")
        username = verify_result.get("username")

    except Exception as e:
        log(50, "auth network error", error=str(e))
        return jsonify({"success": False, "message": "Authentication network error. Please try again later."}), 500

    try:

        auth_response = requests.post(
            f"{AUTH_API_URL}/jwt/assign",
            headers={
                "API-Requested-With": "Home Gateway"
            },
            json={
                "user_id": user_id,
                "username": username
            }
        )

        try:
            auth_result = auth_response.json()
        except Exception:
            log(40, "auth bad response")
            return jsonify({"success": False, "message": "Auth service error"}), 502

        if not auth_response.ok:
            if auth_result.get("forbidden", False):
                log(30, "auth forbidden")
                return jsonify({
                    "success": False,
                    "location": "/unknown",
                    "message": "Forbidden access"
                }), 403

            assign_message = auth_result.get("message", "Failed to assign JWT")
            log(40, "auth error", status_code=auth_response.status_code)
            return jsonify({"success": False, "message": assign_message}), auth_response.status_code

        resp = jsonify({
            "success": True,
            "message": f"Welcome {username}, you are logged in!",
        })

        for cookie in auth_response.cookies:
            resp.set_cookie(
                cookie.name,
                cookie.value,
                **cookie.__dict__.get('_rest', {})  # preserve cookie flags
            )

        return resp, 200

    except Exception as e:
        log(40, "auth jwt assignment error", error=str(e))
        return jsonify({
            "success": False,
            "message": "Auth service error. Please try again later."
        }), 403


@api_auth_bp.route('/logout', methods=['POST'])
def logout():
    access_cookie = request.cookies.get("access_token_cookie")

    if not access_cookie:
        return jsonify({
            "success": False,
            "message": "No active session found"
        }), 400

    try:
        auth_response = requests.post(
            f"{AUTH_API_URL}/jwt/remove",
            cookies=request.cookies,
            headers={
                "API-Requested-With": "Home Gateway"
            }
        )

        return jsonify(auth_response.json()), auth_response.status_code

    except Exception as e:
        log(40, "auth logout error", error=str(e))
        return jsonify({
            "success": False,
            "message": "Logout failed. Please try again."
        }), 500
    
@api_auth_bp.route('/verify', methods=['GET'])
def verify_user():
    try:
        cookies = request.cookies

        resp = requests.get(f"{AUTH_API_URL}/jwt/verify", cookies=cookies, timeout=5)

        # Pass through the response from auth server
        if resp.status_code == 200:
            # Auth server verified JWT
            data = resp.json()
            return jsonify({"success": True, "user_id": data.get("user_id")}), 200
        else:
            # Invalid or expired JWT
            return jsonify({
                "success": False,
                "message": "Unauthorized access. Please log in again."
            }), 401
    except requests.RequestException as e:
        # Network error or auth server down
        return jsonify({
            "success": False,
            "message": "Authentication server unreachable."
        }), 503