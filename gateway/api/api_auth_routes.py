from flask import request, jsonify, Blueprint, g
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
        headers = {"request_id": g.request_id,
                   "API-Requested-With": "Home Gateway"
                   }

        validate_response = requests.post(
            f"{AUTH_API_URL}/user/validate",
            headers=headers,
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
        headers = {"request_id": g.request_id,
                   "API-Requested-With": "Home Gateway"
                   }

        assign_response = requests.post(
            f"{AUTH_API_URL}/jwt/assign",
            headers=headers,
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
        resp.status_code = 201  # hard code status_code on flask response object instead of tuple
                                # as we cannot risk headers being stripped in tuple form

        # Forward Set-Cookie header without modifying it
        if "Set-Cookie" in assign_response.headers:
            resp.headers.add("Set-Cookie", assign_response.headers["Set-Cookie"])

        return resp

    except Exception as e:
        log(40, "auth jwt assignment error", error=str(e))
        return jsonify({
            "success": False,
            "message": "Auth service error. Please try again later."
        }), 403


@api_auth_bp.route('/login', methods=['POST'])
def login():
    if request.headers.get("X-Requested-With") != "ReactApp":
        log(30, "forbidden request received")

        return jsonify({"success": False,
                        "location": "/unknown",
                        "message": "Forbidden access"}), 403

    try:
        data = request.get_json()
    except Exception:
        log(40, "front bad response")
        return jsonify({"success": False, "message": "Bad response. Please try again"}), 502

    try:
        headers = {"request_id": g.request_id,
                   "API-Requested-With": "Home Gateway"
                   }

        verify_response = requests.post(
            f"{AUTH_API_URL}/user/verify",
            headers=headers,
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
        headers = {"request_id": g.request_id,
                   "API-Requested-With": "Home Gateway"
                   }

        auth_response = requests.post(
            f"{AUTH_API_URL}/jwt/assign",
            headers=headers,
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
        resp.status_code = 200

        if "Set-Cookie" in auth_response.headers:
            resp.headers.add("Set-Cookie", auth_response.headers["Set-Cookie"])

        return resp

    except Exception as e:
        log(40, "auth jwt assignment error", error=str(e))
        return jsonify({
            "success": False,
            "message": "Auth service error. Please try again later."
        }), 403


@api_auth_bp.route('/logout', methods=['POST'])
def logout():
    if request.headers.get("X-Requested-With") != "ReactApp":
        log(30, "forbidden request received")
        return jsonify({"success": False,
                        "location": "/unknown",
                        "message": "Forbidden access"}), 403

    access_cookie = request.cookies.get("access_token_cookie")

    if not access_cookie:
        return jsonify({
            "success": False,
            "message": "No active session found"
        }), 400

    try:
        headers = {"request_id": g.request_id,
                   "API-Requested-With": "Home Gateway"
                   }

        cookies = {
            "access_token_cookie": access_cookie
        }

        resp = requests.post(
            f"{AUTH_API_URL}/jwt/remove",
            headers=headers,
            cookies=cookies,
            timeout=5
        )

        forward_resp = jsonify(resp.json())
        forward_resp.status_code = resp.status_code

        log(50, "fsf", status_code=forward_resp.status_code)

        if "Set-Cookie" in resp.headers:
            forward_resp.headers.add("Set-Cookie", resp.headers["Set-Cookie"])

        return forward_resp

    except Exception as e:
        log(50, "auth logout error", error=str(e))
        return jsonify({
            "success": False,
            "message": "Logout failed. Please try again."
        }), 500


@api_auth_bp.route('/verify', methods=['GET'])
def verify_user():
    if request.headers.get("X-Requested-With") != "ReactApp":
        log(30, "forbidden request received")

        return jsonify({"success": False,
                        "location": "/unknown",
                        "message": "Forbidden access"}), 403

    try:
        headers = {"request_id": g.request_id,
                   "API-Requested-With": "Home Gateway"
                   }

        # Forward the exact Cookie header the browser originally sent
        cookies = {
            "access_token_cookie": request.cookies.get("access_token_cookie")
        }

        resp = requests.get(
            f"{AUTH_API_URL}/jwt/verify",
            headers=headers,
            cookies=cookies,
            timeout=5
        )

        try:
            result = resp.json()
        except Exception:
            log(40, "auth bad response")
            return jsonify({"success": False, "message": "auth service error"}), 502

        if not resp.status_code == 200:
            log(40, "auth error", status_code=resp.status_code)
            return jsonify(result), resp.status_code

        return jsonify({"success": True, "user_id": result.get("user_id")}), resp.status_code

    except Exception as e:
        log(40, "auth verify error", error=str(e))
        return jsonify({
            "success": False,
            "message": "Authentication server error."
        }), 503