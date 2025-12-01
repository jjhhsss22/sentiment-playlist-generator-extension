from flask import Blueprint, request, jsonify

from celery_worker import run_prediction_task
from log_logic.log_util import log

ai_bp = Blueprint('ai', __name__)

@ai_bp.route("/predict", methods=["POST"])
def return_prediction():
    try:
        data = request.get_json()
    except Exception:
        log(30, "gateway bad response")
        return jsonify({
            "success": False,
            "message": "Bad response from gateway server. Please try again later."
        }), 502

    origin = data.get("API-Requested-With", "")
    user_id = data.get("user_id")

    if origin != "Home Gateway":
        log(30, "forbidden request received", user_id)
        return jsonify({"forbidden": True}), 403

    input_text = data.get("text", "").strip()
    desired_emotion = data.get("emotion", None)

    try:
        task = run_prediction_task.delay(input_text, desired_emotion)
        return jsonify({"success": True, "task_id": task.id}), 200
    except Exception as e:
        log(50, "failed to start celery task", user_id=user_id, error=str(e))
        return jsonify({
            "success": False,
            "message": "Failed to start AI prediction."
        }), 500


# celery prediction task status
@ai_bp.route("/task/<task_id>", methods=["GET"])
def get_task_status(task_id):
    data = request.get_json()
    user_id = data.get("user_id")

    task = run_prediction_task.AsyncResult(task_id)

    if task.state == "PENDING":
        return jsonify({"status": "pending"}), 202
    elif task.state == "SUCCESS":
        return jsonify({"status": "done", "result": task.result}), 200
    # elif task.state == "FAILURE":
    #     return jsonify({"status": "error", "message": str(task.info)})
    else:
        log(40, "celery task failed", user_id=user_id, task_id=task.id, task_state=task.state)
        return jsonify({"status": task.state}), 500


# AI api server health check
@ai_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200