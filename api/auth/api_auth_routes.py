from flask import request, jsonify, Blueprint, current_app, render_template
from flask_jwt_extended import create_access_token
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

        if verification_response.status_code != 200:
            current_app.logger.error(f"Error status code: {verification_response.status_code}")
            return jsonify({"success": False, "message": "failed to connect to db server "}), 500

        verify_result = verification_response.json()

        if not verify_result.get("success"):
            return jsonify(verify_result), 409

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({"success": False, "message": "Could not connect to user database"}), 500

    try:
        create_response = requests.post(
            f"{DB_API_URL}/new-user",
            json={
                "API-Requested-With": "Home Gateway",
                "email": email,
                "username": username,
                "password": password
            })

        if create_response.status_code != 201:
            current_app.logger.error(f"Error status code: {create_response.status_code}")
            return jsonify({"success": False, "message": "User creation failed"}), 500

        create_result = create_response.json()
        user_id = create_result.get("id")

        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(hours=6))

        return jsonify({"success": True,
                        "message": f"Hello {username}, your account has been created!",
                        "access_token": access_token}), 201

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({"success": False, "message": "Failed to create user"}), 500


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

        if login_response.status_code != 200:
            current_app.logger.error(f"Error status code: {login_response.status_code}")
            return jsonify({"success": False, "message": "Verification failed"}), 500

        login_result = login_response.json()

        if not login_result.get("success"):
            return jsonify(login_result), 401

        user_id = login_result['id']
        access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(hours=6))

        return jsonify({"success": True, "message": f"Welcome {username}, you are logged in",
                        "access_token": access_token}), 200

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return jsonify({"success": False, "message": "Failed to log user in"}), 500


# @api_auth_bp.route('/logout', methods=['POST'])
# @login_required
# def logout():
#     logout_user()
#     return jsonify({"success": True, "message": "Logged out"})