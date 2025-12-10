from flask import Blueprint, request, jsonify, g

from db_service.db_structure.db_module import get_user_info, get_playlists, create_user, create_playlist, save
from log_logic.log_util import log

db_bp = Blueprint('db', __name__)

@db_bp.route('/v1/query', methods=['POST'])
def return_user():
    try:
        data = request.get_json()
    except Exception as e:
        log(40, "gateway bad response", error=e)
        return jsonify({
            "success": False,
            "message": "Bad response from gateway server. Please try again later."
        }), 502

    origin = request.headers.get("API-Requested-With", "")

    if origin != "Auth server":
        log(40, "forbidden request not from auth")
        return jsonify({"forbidden": True}), 403

    email = data.get("email")

    try:
        user = get_user_info(email)

        if not user:
            return jsonify({"success": True, "user": None}), 200

        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "password_hash": user.password  # hashed password
            }
        }), 200

    except Exception as e:
        log(40, "database user query or network error", error=e)
        return jsonify({"success": False, "message": "Internal db server error. Please try again later."}), 500

# @app.route('/verification', methods=['GET', 'POST'])
# def verify_user():
#     data = request.get_json()
#     origin = data.get("API-Requested-With", "")
#
#     if origin != "Home Gateway":
#         return jsonify({"forbidden": True}), 403
#
#     mode = data.get("mode")
#     email = data.get("email")
#
#     try:
#         if mode == "signup":
#             existing_user = get_user_info(email)
#
#             if existing_user:
#                 return jsonify({"success": False, "message": "Email already registered"}), 409
#
#             return jsonify({"success": True, "message": "Email not registered"}), 200
#
#         if mode == "login":
#             username = data.get("username")
#             password = data.get("password")
#
#             user = get_user_info(email)
#
#             if not user:  # verification
#                 return jsonify({"success": False, "message": "Invalid email"}), 401
#
#             if user.username != username:
#                 return jsonify({"success": False, "message": "Invalid username"}), 401
#
#             if not check_password_hash(user.password, password):
#                 return jsonify({"success": False, "message": "Invalid password"}), 401
#
#             return jsonify({"success": True, "message": "Login successful", "id": user.id}), 200
#
#         else:
#             return jsonify({"success": False, "message": "Invalid mode"}), 400
#
#     except Exception:
#         return jsonify({"success": False, "message": "Internal db server error"}), 500


@db_bp.route('/new-user', methods=['POST'])
def new_user():
    try:
        data = request.get_json()
    except Exception as e:
        log(40, "gateway bad response", error=e)
        return jsonify({
            "success": False,
            "message": "Bad response from gateway server. Please try again later."
        }), 502

    origin = request.headers.get("API-Requested-With", "")

    if origin != "Auth server":
        log(40, "forbidden request not from gateway")
        return jsonify({"forbidden": True}), 403

    try:
        email = data.get("email")
        username = data.get("username")
        hashed_password = data.get("hashed_password")

        new_user = create_user(email, username, hashed_password)
        save(new_user)

        return jsonify({"success": True, "message": "User created successfully", "user_id": new_user.id}), 201
    except Exception as e:
        log(40, "database user creation error", error=e)
        return jsonify({"success": False, "message": "Failed to create user"}), 500


@db_bp.route('/playlist', methods=['POST'])
def return_playlists():

    origin = request.headers.get("API-Requested-With", "")

    if origin != "Home Gateway":
        log(40, "forbidden request not from gateway")
        return jsonify({"forbidden": True}), 403

    try:
        playlists_data = get_playlists(g.user_id)
        return jsonify({"success": True, "playlists": playlists_data}), 200
    except Exception as e:
        log(40, "database playlist query error", error=e)
        return jsonify({"success": False, "message": "Playlist database error"}), 500


@db_bp.route('/new-playlist', methods=['POST'])
def new_playlist():
    try:
        data = request.get_json()
    except Exception as e:
        log(40, "gateway bad response")
        return jsonify({
            "success": False,
            "message": "Bad response from gateway server. Please try again later."
        }), 502

    origin = request.headers.get("API-Requested-With", "")

    if origin != "Home Gateway":
        log(40, "forbidden request not from gateway")
        return jsonify({"forbidden": True}), 403

    try:
        input_text = data.get("text")
        likely_emotion = data.get("likely_emotion")
        desired_emotion = data.get("desired_emotion")
        playlist_text = data.get("playlist_text")

        new_playlist = create_playlist(input_text, likely_emotion, desired_emotion, playlist_text, g.user_id)
        save(new_playlist)

        return jsonify({"success": True, "message": "Playlist created successfully"}), 201
    except Exception:
        return jsonify({"success": False, "message": "Failed to create playlist"}), 500