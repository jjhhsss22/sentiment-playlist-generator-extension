from flask import Blueprint, jsonify, request, g
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
    origin = request.headers.get("API-Requested-With", "")

    if origin != "Home Gateway":
        log(50, "forbidden request not from gateway")
        return jsonify({"forbidden": True}), 403

    for _ in range(3):
        try:
            user_id = get_jwt_identity()
            return jsonify({"success": True, "user_id": user_id}), 200
        except Exception as e:
            log(40, "failed to get user id", error=e)

    log(50, "complete failure to verify jwt")
    return jsonify({"success": False, "message": "Failed to authenticate. Please try again."}), 500


@jwt_bp.route("/assign", methods=["POST"])
def assign_jwt():
    origin = request.headers.get("API-Requested-With", "")

    if origin != "Home Gateway":
        log(50, "forbidden request not from gateway")
        return jsonify({"forbidden": True}), 403

    try:
        data = request.get_json()
    except Exception as e:
        log(40, "gateway bad response", error=e)
        return jsonify({"success": False, "message": "Bad response from gateway server. Please try again."}), 502

    username = data.get("username", "")

    if not g.user_id or not username:
        return jsonify({
            "success": False,
            "message": "Invalid information. Please try again."
        }), 400

    try:
        access_token = create_access_token(
            identity=str(g.user_id),
            expires_delta=timedelta(hours=6)
        )

        resp = jsonify({
            "success": True,
            "message": f"Token assigned for {username} with id {str(g.user_id)}.",
        })
        resp.status_code = 200

        set_access_cookies(resp, access_token)
        return resp

    except Exception as e:
        log(50, "failed to assign jwt", error=e)
        return jsonify({"success": False, "message": "Failed to grant access. Please try again."}), 500


@jwt_bp.route("/remove", methods=["POST"])
def remove_jwt():
    origin = request.headers.get("API-Requested-With", "")

    if origin != "Home Gateway":
        log(50, "forbidden request not from gateway")
        return jsonify({"forbidden": True}), 403

    try:
        resp = jsonify({"success": True, "message": "Logged out"})
        resp.status_code = 200
        unset_jwt_cookies(resp)
        return resp
    except Exception as e:
        log(50, "failed to remove jwt", error=e)
        return jsonify({"success": False, "message": "Failed to log out. Please try again."}), 500
