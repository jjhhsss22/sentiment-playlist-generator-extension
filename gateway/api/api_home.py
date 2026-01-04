from flask import current_app, request, jsonify, Blueprint, g
import requests
import time
import redis
import json

from log_logic.log_util import log
from celery_worker import generate_playlist_pipeline  # correct import scope?

api_home_bp = Blueprint('api_home', __name__)

AI_API_URL = "http://127.0.0.1:8001"
MUSIC_API_URL = "http://127.0.0.1:8002/create-playlist"
DB_API_URL = "http://127.0.0.1:8003/new-playlist"
AUTH_API_URL = "http://127.0.0.1:8004/jwt/verify"


def get_redis_cache():  # used in home route
    return current_app.extensions.get("redis_cache")


@api_home_bp.route('/home', methods=['GET', 'POST'])
def home():
    if request.headers.get("X-Requested-With") != "ReactApp":
        log(30, "forbidden request received")

        return jsonify({"success": False,
                        "location": "/unknown",
                        "message": "Forbidden access"}), 403

# AUTH ---------------------------------------------------------------------

    try:
        headers = {"request-id": g.request_id,
                   "API-Requested-With": "Home Gateway"
                   }

        cookies = {
            "access_token_cookie": request.cookies.get("access_token_cookie")
        }

        auth_response = requests.get(
            AUTH_API_URL,
            headers=headers,
            cookies=cookies,
            timeout=5
        )

        try:
            auth_results = auth_response.json()
        except Exception as e:
            log(40, "auth bad response", error=e)
            return jsonify({
                "success": False,
                "message": "Bad response from authentication server. Please try again."
            }), 502

        if auth_response.status_code != 200:
            if auth_results.get("forbidden", False):
                log(40, "auth forbidden")
                return jsonify({"success": False,
                                "location": "/unknown",
                                "message": "Forbidden access"}), 403

            log(40, "auth error", status_code=auth_response.status_code)
            return auth_results, auth_response.status_code

        user_id = auth_results.get("user_id")
        g.user_id = user_id

    except Exception as e:
        log(50, "auth server network error", error=e)
        return jsonify({
            "success": False,
            "message": "Authentication server error. Please try again."
        }), 500

# AUTH ---------------------------------------------------------------------

    data = request.get_json()
    input_text = data.get("text", "").strip()
    desired_emotion = data.get("emotion", None)

    redis_cache = get_redis_cache()

    if redis_cache is None:
        log(40, "redis cache is None")
    else:
        cache_key = f"playlist:result:{g.request_id}"
        cached = redis_cache.get(cache_key)  # from init

        if cached:
            log(20, f"cache hit for request_id={g.request_id} from user={user_id}")
            return jsonify(json.loads(cached)), 200

    task = generate_playlist_pipeline.delay(
        input_text,
        desired_emotion,
        g.user_id,
        g.request_id
    )

    return jsonify({
        "success": True,
        "task_id": task.id,
        "request_id": g.request_id,
        "status": "processing"
    }), 202


# @api_home_bp.route('/home', methods=['GET', 'POST'])
# def home():
#     start_time = time.time()
#
#     if request.headers.get("X-Requested-With") != "ReactApp":
#         log(30, "forbidden request received")
#
#         return jsonify({"success": False,
#                         "location": "/unknown",
#                         "message": "Forbidden access"}), 403
#
# # Auth ------------------------------------------------------------------------
#
#     try:
#         headers = {"request-id": g.request_id,
#                    "API-Requested-With": "Home Gateway"
#                    }
#
#         cookies = {
#             "access_token_cookie": request.cookies.get("access_token_cookie")
#         }
#
#         auth_response = requests.get(
#             AUTH_API_URL,
#             headers=headers,
#             cookies=cookies,
#             timeout=5
#         )
#
#         try:
#             auth_results = auth_response.json()
#         except Exception as e:
#             log(40, "auth bad response", error=e)
#             return jsonify({
#                 "success": False,
#                 "message": "Bad response from authentication server. Please try again."
#             }), 502
#
#         if auth_response.status_code != 200:
#             if auth_results.get("forbidden", False):
#                 log(40, "auth forbidden")
#                 return jsonify({"success": False,
#                                 "location": "/unknown",
#                                 "message": "Forbidden access"}), 403
#
#             log(40, "auth error", status_code=auth_response.status_code)
#             return auth_results, auth_response.status_code
#
#         user_id = auth_results.get("user_id")
#         g.user_id = user_id
#
#     except Exception as e:
#         log(50, "auth server network error", error=e)
#         return jsonify({
#             "success": False,
#             "message": "Authentication server error. Please try again."
#         }), 500
#
# # AI ------------------------------------------------------------------------
#
#     try:
#         data = request.get_json()
#         input_text = data.get("text", "").strip()
#         desired_emotion = data.get("emotion", None)
#
#         headers = {"request-id": g.request_id,
#                    "user-id": str(g.user_id),
#                    "API-Requested-With": "Home Gateway"
#                    }
#         # no need for IP whitelisting or internal secret key
#         # because api servers only accessible from this gateway server por other internal servers
#
#         ai_response = requests.post(
#             f"{AI_API_URL}/predict",
#             headers=headers,
#             json={
#             "text": input_text,
#             "emotion": desired_emotion
#             },
#             timeout=5
#         )
#
#         try:
#             ai_results = ai_response.json()
#         except Exception as e:
#             log(40, "AI bad response", error=e)
#             return jsonify({
#                 "success": False,
#                 "message": "Bad response from AI server. Please try again."
#             }), 502
#
#         if not ai_response.ok:
#             if ai_results.get("forbidden", False):
#                 log(40, "AI forbidden")
#                 return jsonify({"success": False,
#                                 "location": "/unknown",
#                                 "message": "Forbidden access"}), 403
#
#             log(40, "AI error", status_code=ai_response.status_code)
#             ai_message = ai_results.get("message", "Error when retrieving prediction. Please try again later.")
#             return jsonify({"success": False, "message": ai_message}), ai_response.status_code
#
#         task_id = ai_results.get("task_id")
#
#         for _ in range(16):  # retry for 8 seconds
#
#             '''
#             simple setup for now as AI most likely won't take more than 5 seconds
#             but should setup another celery task form this gateway server to constantly poll the AI task until it's done
#             '''
#
#             time.sleep(0.5)
#             status_resp = requests.get(f"{AI_API_URL}/task/{task_id}", timeout=5)
#
#             try:
#                 status_data = status_resp.json()
#             except Exception as e:
#                 log(40, "AI celery task bad response", error=e)
#                 continue
#
#             if status_data.get("status") == "done":
#                 ai_data = status_data["result"]
#
#                 if ai_data.get("success") is False:
#                     log(50, "AI celery task error", status_code=ai_data.get("status_code"))
#                     return jsonify({
#                         "success": False,
#                         "message": ai_data.get("message", "Error when predicting emotion. Please try again.")
#                     }), ai_data.status_code
#
#                 predictions_list = ai_data["predictions_list"]
#                 predicted_emotions = ai_data["predicted_emotions"]
#                 likely_emotion = ai_data["likely_emotion"]
#                 starting_coord = ai_data["starting_coord"]
#                 target_coord = ai_data["target_coord"]
#                 others_probability = ai_data["others_probability"]
#
#                 break
#
#             # if status_data.get("status") == "error":
#             #     current_app.logger.error(f"AI Celery task error: {status_data["result"].get("message", "")}")
#
#         else:
#             log(40, "AI celery task timeout")
#             return jsonify({
#                 "success": False,
#                 "message": "Prediction timed out. Please try again."
#             }), 408
#
#     except Exception as e:  # handle network errors
#         log(50, "AI celery task network error", error=e)
#         return jsonify({
#             "success": False,
#             "message": "AI server error. Please try again."
#         }), 500
#
# # MUSIC ------------------------------------------------------------------------
#
#     try:
#         headers = {"request-id": g.request_id,
#                    "user-id": str(g.user_id),
#                    "API-Requested-With": "Home Gateway"
#                    }
#
#         music_response = requests.post(
#             MUSIC_API_URL,
#             headers=headers,
#             json={
#             "starting_coord": starting_coord,
#             "target_coord": target_coord,
#             },
#             timeout=5
#         )
#
#         try:
#             music_results = music_response.json()
#         except Exception as e:
#             log(40, "music bad response", error=e)
#             return jsonify({
#                 "success": False,
#                 "message": "Bad response from music server. Please try again."
#             }), 502
#
#         if not music_response.ok:
#             if music_results.get("forbidden", False):
#                 log(40, "music forbidden")
#                 return jsonify({"success": False,
#                                 "location": "/unknown",
#                                 "message": "Forbidden access"}), 403
#
#             log(40, "music error", status_code=music_response.status_code)
#             music_message = music_results.get("message", "Error when generating playlist. Please try again.")
#             return jsonify({"success": False, "message": music_message}), music_response.status_code
#
#         music_data = music_results["result"]
#         playlist_list = music_data["list"]
#         playlist_text = music_data["text"]
#
#         if len(playlist_list) <= 2:
#             log(20, "music no songs")  # just in case something wrong with the algorithm
#             return jsonify({
#                 "success": False,
#                 "message": "No available songs with the provided emotions. You are already near your desired emotion!"
#             }), 200
#
#     except Exception as e:  # handle network errors
#         log(50, "music network error", error=e)
#         return jsonify({
#             "success": False,
#             "message": "Music server error. Please try again."
#             }), 500
#
# # DB ------------------------------------------------------------------------
#
#     try:
#         headers = {"request_id": g.request_id,
#                    "user_id": str(g.user_id),
#                    "API-Requested-With": "Home Gateway"
#                    }
#
#         db_response = requests.post(
#             DB_API_URL,
#             headers=headers,
#             json={
#                 "text": input_text,
#                 "likely_emotion": likely_emotion,
#                 "desired_emotion": desired_emotion,
#                 "playlist_text": playlist_text,
#                 },
#                 timeout=5
#             )
#
#         try:
#             db_results = db_response.json()
#         except Exception as e:
#             log(40, "db bad response", error=e)
#             return jsonify({
#                 "success": False,
#                 "message": "Bad response from database server. Please try again."
#             }), 502
#
#         if not db_response.ok:
#             if db_results.get("forbidden", False):
#                 log(40, "db forbidden")
#                 return jsonify({"success": False,
#                                 "location": "/unknown",
#                                 "message": "Forbidden access"}), 403
#
#             log(40, "db error", status_code=db_response.status_code)
#             db_message = db_results.get("message", "Error when saving playlist. Please try again.")
#             return jsonify({"success": False, "message": db_message}), db_response.status_code
#
#         total_time = round(time.time() - start_time, 3)
#         log(20, "pipeline success", time=total_time)
#
#         return jsonify({
#             "success": True,
#             "message": "Playlist generated successfully!",
#             "desired_emotion": desired_emotion,
#             "songs_playlist": playlist_list,
#             "predicted_emotions": predicted_emotions,
#             "predictions_list": predictions_list,
#             "others_prediction": others_probability
#         }), 200
#
#     except Exception as e:  # handle network errors
#         log(50, "db network error", error=e)
#         return jsonify({
#             "success": False,
#             "message": "Database server error. Please try again."
#         }), 500
