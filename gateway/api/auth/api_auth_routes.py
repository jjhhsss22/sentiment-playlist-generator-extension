from flask import request, jsonify, Blueprint, current_app, render_template
from flask_jwt_extended import create_access_token, set_access_cookies
from datetime import timedelta
import requests
from werkzeug.security import check_password_hash, generate_password_hash

from gateway.log_logic.log_util import log
from gateway.api.auth.auth_verification import is_valid_username, is_valid_password

api_auth_bp = Blueprint('api_auth', __name__)

DB_API_URL = "http://127.0.0.1:8003"

@api_auth_bp.route('/signup', methods=['POST'])
def signup():
    if request.headers.get("X-Requested-With") != "ReactApp":
        log(30, "forbidden request received")
        return render_template("unknown.html"), 403

    try: data = request.get_json()  # data from the form
    except Exception:
        log(40, "front bad response")
        return jsonify({"success": False, "message": "Invalid request. Please try again"}), 400

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')  # id from the HTML file

    if not is_valid_username(username):
        return jsonify({"success": False, "message": "Invalid username — cannot contain spaces."}), 401

    if not is_valid_password(password, confirm_password):
        return jsonify({"success": False, "message": "Invalid password or mismatch."}), 401

    try:
        query_response = requests.post(
            f"{DB_API_URL}/v1/query",
            json={
                "API-Requested-With": "Home Gateway",
                "email": email
            })

        try:
            query_result = query_response.json()
        except Exception:
            log(40, "db bad response")
            return jsonify({"success": False, "message": "Database server error"}), 502

        if not query_response.ok:
            if query_result.get("forbidden", False):
                log(30, "db forbidden")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            verify_message = query_result.get("message", "Failed to access database")
            log(40, "db error", status_code=query_response.status_code)
            return jsonify({"success": False, "message": verify_message}), query_response.status_code

        if query_result.get("user"):
            return jsonify({"success": False, "message": "Email already registered"}), 409

    except Exception as e:
        log(50, "db network error", error=str(e))
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500

    try:
        hashed_password = generate_password_hash(password)

        create_response = requests.post(
            f"{DB_API_URL}/new-user",
            json={
                "API-Requested-With": "Home Gateway",
                "email": email,
                "username": username,
                "hashed_password": hashed_password
            })

        try:
            create_result = create_response.json()
        except Exception:
            log(40, "db bad response")
            return jsonify({"success": False, "message": "Database server error"}), 502

        if not create_response.ok:
            if create_result.get("forbidden", False):
                log(30, "db forbidden")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            create_message = create_result.get("message", "Failed to create new user")
            log(40, "db error", status_code=create_response.status_code)
            return jsonify({"success": False, "message": create_message}), create_response.status_code

        user_id = create_result.get("id")
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(hours=6))

        resp = jsonify({"success": True,
                        "message": f"Hello {username}, your account has been created!"})
        set_access_cookies(resp, access_token)

        return resp, 201

    except Exception as e:
        log(50, "db network error", error=str(e))
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500


@api_auth_bp.route('/login', methods=['POST'])
def login():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return render_template("unknown.html"), 403

    try: data = request.get_json()
    except Exception:
        log(40, "front bad response")
        return jsonify({"success": False, "message": "Invalid request. Please try again"}), 400

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    try:
        query_response = requests.post(
            f"{DB_API_URL}/v1/query",
            json={
                "API-Requested-With": "Home Gateway",
                "email": email
            })

        try:
            query_result = query_response.json()
        except Exception:
            log(40, "db bad response")
            return jsonify({"success": False, "message": "Database server error"}), 502

        if not query_response.ok:
            if query_result.get("forbidden", False):
                log(30, "db forbidden")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            verify_message = query_result.get("message", "Failed to access database")
            log(40, "db error", status_code=query_response.status_code)
            return jsonify({"success": False, "message": verify_message}), query_response.status_code

        user = query_result.get("user")

        if not user:
            return jsonify({"success": False, "message": "Invalid email"}), 401

        if user["username"] != username:
            return jsonify({"success": False, "message": "Invalid username"}), 401

        if not check_password_hash(user["password_hash"], password):
            return jsonify({"success": False, "message": "Invalid password"}), 401

        user_id = user['id']
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(hours=6))

        resp = jsonify({"success": True,
                        "message": f"Welcome {username}, you are logged in!"})
        set_access_cookies(resp, access_token)

        return resp, 200

    except Exception as e:
        log(50, "db network error", error=str(e))
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500


# @api_auth_bp.route('/logout', methods=['POST'])
# @login_required
# def logout():
#     logout_user()
#     return jsonify({"success": True, "message": "Logged out"})