from flask import Flask, request, jsonify

from music_logic.music_module import generate_playlist_pipeline

app = Flask(__name__)

@app.route('/playlist', methods=['POST'])
def return_playlist():
    data = request.get_json()
    origin = data.get("API-Requested-With", "")
    starting_coord = data.get("starting_coord")
    target_coord = data.get("target_coord")

    if origin != "Home Gateway":
        return jsonify({"forbidden": True}), 403

    try:
        result = generate_playlist_pipeline(starting_coord, target_coord)
        return jsonify({"success": True, "result": result}), 200
    except Exception:  # no need for detailed error messaging for the music service
        return jsonify({"success": False, "message": "music server error. Please try again later"}), 500


if __name__ == "__main__":
    app.run(port=8002, debug=True)