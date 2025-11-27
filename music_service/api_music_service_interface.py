from flask import Flask, request, jsonify

from music_logic.music_module import generate_playlist_pipeline
from log_logic.log_util import log
from ms_init import create_ms

app = create_ms()

@app.route('/create-playlist', methods=['POST'])
def return_playlist():
    data = request.get_json()
    origin = data.get("API-Requested-With", "")
    starting_coord = data.get("starting_coord")
    target_coord = data.get("target_coord")

    if origin != "Home Gateway":
        log(30, "forbidden request received")
        return jsonify({"forbidden": True}), 403

    try:
        result = generate_playlist_pipeline(starting_coord, target_coord)
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:  # no need for detailed error messaging for the music service
        log(40, "forbidden request received", error=str(e))
        return jsonify({"success": False, "message": "music server error. Please try again later"}), 500


if __name__ == "__main__":
    app.run(port=8002, debug=True)