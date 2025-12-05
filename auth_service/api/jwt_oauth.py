from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies,
    create_access_token,
    set_access_cookies
)
from datetime import timedelta

from log_logic.log_util import log

jwt_bp = Blueprint('jwt', __name__)


@jwt_bp.route("/verify", methods=["GET"])
@jwt_required()
def verify_jwt():
    user_id = get_jwt_identity()
    return jsonify({"success": True, "user_id": user_id}), 200


@jwt_bp.route("/assign", methods=["POST"])
def assign_jwt():
    data = request.get_json()

    user_id = data.get("user_id")
    username = data.get("username", "")

    if not user_id or not username:
        return jsonify({
            "success": False,
            "message": "Missing user id or username"
        }), 400

    try:
        access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(hours=6)
        )

        resp = jsonify({
            "success": True,
            "message": f"Token assigned for {username} with id {user_id}",
        })
        resp.status_code = 200

        set_access_cookies(resp, access_token)
        return resp

    except Exception as e:
        log(50, "failed to assign jwt", error=e)
        return jsonify({"success": False, "message": "failed to grant access. Please try again"}), 500


@jwt_bp.route("/remove", methods=["POST"])
def remove_jwt():
    try:
        resp = jsonify({"success": True, "message": "Logged out"})
        resp.status_code = 200
        unset_jwt_cookies(resp)
        return resp
    except Exception as e:
        log(50, "failed to remove jwt", error=e)
        return jsonify({"success": False, "message": "failed to log out. Please try again."}), 500
