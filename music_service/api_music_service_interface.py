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
        return jsonify({"forbidden": True})

    try:
        result = generate_playlist_pipeline(starting_coord, target_coord)
        return jsonify({"success": True, "result": result})
    except Exception:
        return jsonify({"success": False, "message": "music_service server error. Please try again later"})


if __name__ == "__main__":
    app.run(port=8002, debug=True)