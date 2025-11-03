from werkzeug.security import check_password_hash
from flask import request, jsonify

from db_service.db_structure.db_module import get_user_info, get_playlists, create_user, create_playlist, save
from db_init import create_db

app = create_db()

@app.route('/verification', methods=['GET', 'POST'])
def verify_user():
    data = request.get_json()
    origin = data.get("API-Requested-With", "")

    if origin != "Home Gateway":
        return jsonify({"forbidden": True}), 403

    mode = data.get("mode")
    email = data.get("email")

    try:
        if mode == "signup":
            existing_user = get_user_info(email)

            if existing_user:
                return jsonify({"success": False, "message": "Email already registered"}), 409

            return jsonify({"success": True, "message": "Email not registered"}), 200

        if mode == "login":
            username = data.get("username")
            password = data.get("password")

            user = get_user_info(email)

            if not user:  # verification
                return jsonify({"success": False, "message": "Invalid email"}), 404

            if user.username != username:
                return jsonify({"success": False, "message": "Invalid username"}), 401

            if not check_password_hash(user.password, password):
                return jsonify({"success": False, "message": "Invalid password"}), 401

            return jsonify({"success": True, "message": "Login successful", "id": user.id}), 200

        else:
            return jsonify({"success": False, "message": "Invalid mode"}), 400

    except Exception:
        return jsonify({"success": False, "message": "Internal server error"}), 500



@app.route('/new-user', methods=['POST'])
def new_user():
    data = request.get_json()

    origin = data.get("API-Requested-With", "")

    if origin != "Home Gateway":
        return jsonify({"forbidden": True}), 403

    try:
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

        new_user = create_user(email, username, password)
        save(new_user)

        return jsonify({"success": True, "message": "User created successfully", "id": new_user.id}), 201
    except Exception:
        return jsonify({"success": False, "message": "Failed to create user"}), 500


@app.route('/new-playlist', methods=['POST'])
def new_playlist():
    data = request.get_json()

    try:
        input_text = data.get("text")
        likely_emotion = data.get("likely_emotion")
        desired_emotion = data.get("desired_emotion")
        playlist_text = data.get("playlist_text")
        user_id = data.get("user_id")

        new_playlist = create_playlist(input_text, likely_emotion, desired_emotion, playlist_text, user_id)
        save(new_playlist)

        return jsonify({"success": True, "message": "Playlist created successfully"}), 201
    except Exception:
        return jsonify({"success": "false", "message": "Failed to create playlist"}), 500


@app.route('/playlist', methods=['POST'])
def return_playlists():
    data = request.get_json()
    origin = data.get("API-Requested-With", "")

    if origin != "Home Gateway":
        return jsonify({"forbidden": True}), 403

    user_id = data.get("user_id")

    try:
        playlists_data = get_playlists(user_id)
    except Exception:
        return jsonify({"success": False, "message": "Playlist database error" }), 500

    return jsonify({"success": True, "playlists": playlists_data}), 200


if __name__ == "__main__":
    app.run(port=8003, debug=True)