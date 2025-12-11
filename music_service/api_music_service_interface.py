from flask import Blueprint, request, jsonify

from music_logic.music_module import generate_playlist_pipeline
from log_logic.log_util import log

ms_bp = Blueprint("ms", __name__)

@ms_bp.route('/create-playlist', methods=['POST'])
def return_playlist():
    try:
        data = request.get_json()
    except Exception as e:
        log(40, "gateway bad response", error=e)
        return jsonify({
            "success": False,
            "message": "Bad response from gateway server. Please try again."
        }), 502

    origin = request.headers.get("API-Requested-With", "")

    if origin != "Home Gateway":
        log(50, "forbidden request not from gateway")
        return jsonify({"forbidden": True}), 403

    starting_coord = data.get("starting_coord")
    target_coord = data.get("target_coord")

    try:
        result = generate_playlist_pipeline(starting_coord, target_coord)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        log(50, "playlist generation algorithm failure", error=e)
        return jsonify({"success": False, "message": "Playlist generation failed. Please try again."}), 500