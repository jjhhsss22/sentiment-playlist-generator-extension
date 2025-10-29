from flask import request, jsonify, Blueprint, current_app, render_template
from flask_login import login_user
from werkzeug.security import check_password_hash

from database.repository_interface import create_user, save, find_user_by_email
from api.auth.auth_verification import is_valid_username, is_valid_password


api_auth_bp = Blueprint('api_auth', __name__)

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

    exists = find_user_by_email(email)

    if exists:
        return jsonify({"success": False, "message": "Email already linked to an account."})

    elif not is_valid_username(username):
        return jsonify({"success": False, "message": "Invalid username — cannot contain spaces."})

    elif not is_valid_password(password, confirm_password):
        return jsonify({"success": False, "message": "Invalid password or mismatch."})

    else:
        new_user = create_user(email,
                               username,
                               password)
        save(new_user)

        login_user(new_user, remember=True)  # user session created with LoginManager

        return jsonify({"success": True,
                        "message": f"{username}, your account has been created!"})


@api_auth_bp.route('/login', methods=['POST'])
def login():
    if request.headers.get("X-Requested-With") != "ReactApp":
        current_app.logger.warning(f"Forbidden access: 403")

        return render_template("unknown.html"), 403

    data = request.get_json()

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    user = find_user_by_email(email)

    if not user:  # verification
        return jsonify({"success": False, "message": "Invalid email"})
    elif not user.username == username:
        return jsonify({"success": False, "message": "Invalid username"})
    elif not check_password_hash(user.password, password):
        return jsonify({"success": False, "message": "Invalid password"})
    else:
        login_user(user, remember=True)
        return jsonify({"success": True, "message": f"Welcome {username}, you are logged in"})


# @api_auth_bp.route('/logout', methods=['POST'])
# @login_required
# def logout():
#     logout_user()
#     return jsonify({"success": True, "message": "Logged out"})