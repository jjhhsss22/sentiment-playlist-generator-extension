import os
from flask import Flask, request, jsonify

from celery_worker import run_prediction_task
from log_logic.log_util import log
from ai_init import create_ais

app = create_ais()

@app.route("/predict", methods=["POST"])
def return_prediction():
    data = request.get_json()
    origin = data.get("API-Requested-With", "")
    input_text = data.get("text", "").strip()
    desired_emotion = data.get("emotion", None)

    if origin != "Home Gateway":
        return jsonify({"forbidden": True}), 403

    task = run_prediction_task.delay(input_text, desired_emotion)
    return jsonify({"success": True, "task_id": task.id}), 200



# celery prediction task status
@app.route("/task/<task_id>", methods=["GET"])
def get_task_status(task_id):
    task = run_prediction_task.AsyncResult(task_id)

    if task.state == "PENDING":
        return jsonify({"status": "pending"}), 202
    elif task.state == "SUCCESS":
        return jsonify({"status": "done", "result": task.result}), 200
    # elif task.state == "FAILURE":
    #     return jsonify({"status": "error", "message": str(task.info)})
    else:
        return jsonify({"status": task.state}), 500


# AI api server health check
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    app.run(host="0.0.0.0", port=port, debug=False)