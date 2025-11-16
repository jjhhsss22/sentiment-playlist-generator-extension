from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies

jwt_bp = Blueprint('jwt', __name__)


@jwt_bp.route("/validate", methods=["GET"])
@jwt_required()
def validate():
    user_id = get_jwt_identity()
    return jsonify({"user_id": user_id}), 200

@jwt_bp.route("/logout", methods=["POST"])
def logout():
    resp = jsonify({"message": "Logged out"})
    unset_jwt_cookies(resp)
    return resp, 200