from flask import Blueprint, jsonify, request, g
import requests
from werkzeug.security import check_password_hash, generate_password_hash

from log_logic.log_util import log
from .auth_logic.auth_verification import is_valid_username, is_valid_password, is_valid_email


user_auth_bp = Blueprint('user_auth', __name__)

DB_API_URL = "http://127.0.0.1:8003"

@user_auth_bp.route('/validate', methods=['POST'])
def validate():
    try:
        data = request.get_json()
    except Exception as e:
        log(40, "gateway bad response", error=e)
        return jsonify({"success": False, "message": "Bad response from gateway server. Please try again later."}), 502

    origin = request.headers.get("API-Requested-With", "")

    if origin != "Home Gateway":
        log(50, "forbidden request not from gateway")
        return jsonify({"forbidden": True}), 403

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    confirm = data.get("confirmPassword")

    if not is_valid_email(email):
        return jsonify({
            "success": False,
            "message": "Invalid email."
        }), 401

    if not is_valid_username(username):
        return jsonify({
            "success": False,
            "message": "Invalid username — cannot contain spaces."
        }), 401

    if not is_valid_password(password, confirm):
        return jsonify({
            "success": False,
            "message": "Invalid password or mismatch with password confirmation."
        }), 401

    try:
        headers = {"request-id": g.request_id,
                   "API-Requested-With": "Auth server"
                   }

        query_response = requests.post(
            f"{DB_API_URL}/v1/query",
            headers=headers,
            json={
                "email": email
            })

        try:
            query_result = query_response.json()
        except Exception as e:
            log(40, "db bad response", error=e)
            return jsonify({"success": False, "message": "Bad response from database server. Please try again later."}), 502

        if not query_response.ok:
            if query_result.get("forbidden", False):
                log(40, "db forbidden")
                return jsonify({"forbidden": True}), 403

            query_message = query_result.get("message", "Failed to access database")
            log(40, "db error", status_code=query_response.status_code)
            return jsonify({"success": False, "message": query_message}), query_response.status_code

        if query_result.get("user"):
            return jsonify({"success": False, "message": "Email already registered"}), 409

    except Exception as e:
        log(50, "db network error", error=e)
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500

    try:
        headers = {"request-id": g.request_id,
                   "API-Requested-With": "Auth server"
                   }

        hashed_password = generate_password_hash(password)

        create_response = requests.post(
            f"{DB_API_URL}/new-user",
            headers=headers,
            json={
                "email": email,
                "username": username,
                "hashed_password": hashed_password
            })

        try:
            create_result = create_response.json()
        except Exception:
            log(40, "db bad response")
            return jsonify({"success": False, "message": "Bad response from database server. Please try again later."}), 502

        if not create_response.ok:
            if create_result.get("forbidden", False):
                log(40, "db forbidden")
                return jsonify({"forbidden": True}), 403

            create_message = create_result.get("message", "Failed to create new user")
            log(40, "db error", status_code=create_response.status_code)
            return jsonify({"success": False, "message": create_message}), create_response.status_code

        return create_result, 201

    except Exception as e:
        log(50, "db network error", error=str(e))
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500


@user_auth_bp.route('/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json()
    except Exception as e:
        log(40, "gateway bad response", error=e)
        return jsonify({"success": False, "message": "Bad response from gateway server. Please try again later."}), 502

    origin = request.headers.get("API-Requested-With", "")

    if origin != "Home Gateway":
        log(50, "forbidden request not from gateway")
        return jsonify({"forbidden": True}), 403

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    try:
        headers = {"request-id": g.request_id,
                   "API-Requested-With": "Auth server"
                   }

        db_response = requests.post(
            f"{DB_API_URL}/v1/query",
            headers=headers,
            json={
                "email": email
            })

        try:
            db_result = db_response.json()
        except Exception as e:
            log(40, "db service bad response", error=e)
            return jsonify({"success": False, "message": "Bad response from database server. Please try again later."}), 502

        if not db_response.ok:
            if db_result.get("forbidden"):
                log(40, "db forbidden")
                return jsonify({"forbidden": True}), 403

            db_message = db_result.get("message", "Failed to access authentication server")
            log(40, "auth error", status_code=db_response.status_code)
            return jsonify({"success": False, "message": db_message}), db_response.status_code

    except Exception as e:
        log(50, "db network error", error=e)
        return jsonify({"success": False, "message": "Database network error. Please try again later."}), 500

    user = db_result.get("user")

    if not user:
        return jsonify({"success": False, "message": "Invalid email"}), 401

    if user["username"] != username:
        return jsonify({"success": False, "message": "Invalid username"}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "message": "Invalid password"}), 401

    return jsonify({
        "success": True,
        "user_id": user["id"],
        "username": user["username"]
    }), 200