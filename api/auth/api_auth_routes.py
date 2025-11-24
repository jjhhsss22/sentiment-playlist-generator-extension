from flask import request, jsonify, Blueprint, current_app, render_template
from flask_jwt_extended import create_access_token, set_access_cookies
from datetime import timedelta
import requests

from api.auth.auth_verification import is_valid_username, is_valid_password

api_auth_bp = Blueprint('api_auth', __name__)

DB_API_URL = "http://127.0.0.1:8003"

@api_auth_bp.route('/signup', methods=['POST'])
def signup():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return render_template("unknown.html"), 403

    data = request.get_json()  # data from the form

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')  # id from the HTML file

    if not is_valid_username(username):
        return jsonify({"success": False, "message": "Invalid username — cannot contain spaces."})

    if not is_valid_password(password, confirm_password):
        return jsonify({"success": False, "message": "Invalid password or mismatch."})

    try:
        verification_response = requests.post(
            f"{DB_API_URL}/verification",
            json={
                "API-Requested-With": "Home Gateway",
                "mode": "signup",
                "email": email
            })

        try:
            verify_result = verification_response.json()
        except Exception:
            current_app.logger.error(f"bad response from db server during verification: {verification_response.status_code}")
            return jsonify({"success": False, "message": "Database server error"}), 502

        if not verification_response.ok:
            if verify_result.get("forbidden", False):
                current_app.logger.warning(f"Forbidden access to db server: 403")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            verify_message = verify_result.get("message", "Failed to authenticate")
            current_app.logger.error(f"Error status code: {verification_response.status_code}")
            return jsonify({"success": False, "message": verify_message}), verification_response.status_code

    except Exception as e:
        current_app.logger.error(f"Verification error: {e}")
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500

    try:
        create_response = requests.post(
            f"{DB_API_URL}/new-user",
            json={
                "API-Requested-With": "Home Gateway",
                "email": email,
                "username": username,
                "password": password
            })

        try:
            create_result = create_response.json()
        except Exception:
            current_app.logger.error(f"bad response from db server during user creation: {create_response.status_code}")
            return jsonify({"success": False, "message": "Database server error"}), 502

        if not create_response.ok:
            if create_result.get("forbidden", False):
                current_app.logger.warning(f"Forbidden access to db server: 403")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            create_message = create_result.get("message", "Failed to create new user")
            current_app.logger.error(f"Error status code: {create_response.status_code}")
            return jsonify({"success": False, "message": create_message}), create_response.status_code

        user_id = create_result.get("id")
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(hours=6))

        resp = jsonify({"success": True,
                        "message": f"Hello {username}, your account has been created!"})
        set_access_cookies(resp, access_token)

        return resp, 201

    except Exception as e:
        current_app.logger.error(f"User creation error: {e}")
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500


@api_auth_bp.route('/login', methods=['POST'])
def login():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return render_template("unknown.html"), 403

    data = request.get_json()

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    try:
        login_response = requests.post(
            f"{DB_API_URL}/verification",
            json={
                "API-Requested-With": "Home Gateway",
                "mode": "login",
                "email": email,
                "username": username,
                "password": password
            })

        try:
            login_result = login_response.json()
        except Exception:
            current_app.logger.error(f"bad response from db server during user creation: {login_response.status_code}")
            return jsonify({"success": False, "message": "Database server error"}), 502

        if not login_response.ok:
            if login_result.get("forbidden", False):
                current_app.logger.warning(f"Forbidden access to db server: 403")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            login_message = login_result.get("message", "Failed to log user in")
            current_app.logger.error(f"Error status code: {login_response.status_code}")
            return jsonify({"success": False, "message": login_message}), login_response.status_code

        user_id = login_result['id']
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(hours=6))

        resp = jsonify({"success": True, "message": f"Welcome {username}, you are logged in"})
        set_access_cookies(resp, access_token)

        return resp, 200

    except Exception as e:
        current_app.logger.error(f"Login error: {e}")
        return jsonify({"success": False, "message": "Database server error. Please try again later."}), 500


# @api_auth_bp.route('/logout', methods=['POST'])
# @login_required
# def logout():
#     logout_user()
#     return jsonify({"success": True, "message": "Logged out"})