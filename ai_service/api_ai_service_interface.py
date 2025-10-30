from flask import Flask, request, jsonify
from tensorflow.errors import InvalidArgumentError

from deployment.ai_module import run_prediction_pipeline

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def return_prediction():
    data = request.get_json()
    origin = data.get("API-Requested-With", "")
    input_text = data.get("text", "").strip()
    desired_emotion = data.get("emotion", None)

    if origin != "Home Gateway":
        return jsonify({"forbidden": True})

    try:
        result = run_prediction_pipeline(input_text, desired_emotion)
        return jsonify({"success": True, "result": result})
    except InvalidArgumentError:
        return jsonify({"success": False, "message": "Please submit text in full sentences"})
    except Exception:
        return jsonify({"success": False, "message": "ai server error. Please try again later"})


if __name__ == "__main__":
    app.run(port=8001, debug=True)