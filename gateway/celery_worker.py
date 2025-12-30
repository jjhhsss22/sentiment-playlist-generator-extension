from celery import Celery, signature
from celery import chain
import os
import sys
from log_logic.log_util import task_log

# sys.path.append("/app")  # for docker

# redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_url = "redis://localhost:6379/0"

celery = Celery(
    "gateway",
    broker=redis_url,
    backend=redis_url,
)

celery.conf.task_routes = {
    "gateway.*": {"queue": "gateway"}
}

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=True,
)

@celery.task(name="gateway.full_playlist_generation_pipeline", bind=True)
def generate_playlist_pipeline(self, text, desired_emotion, user_id, request_id):

    pipeline_data = {
        "text": text,
        "desired_emotion": desired_emotion,
        "user_id": user_id,
        "request_id": request_id,
    }

    workflow = chain(
        celery.signature("ai.predict_emotion", args=(pipeline_data,)),
        celery.signature("music.generate_playlist"),
        celery.signature("gateway.finalise_playlist"),
    )  # chain = output of previous celery task --> input of next celery task

    result = workflow.apply_async()
    return {
        "id": result.parent.id if result.parent else result.id
        }

@celery.task(name="gateway.finalise_playlist", bind=True)
def finalise_playlist(self, pipeline_data):

    final_result = {
        "success": True,
        "message": "Playlist generated successfully!",
        "desired_emotion": pipeline_data["ai_result"]["desired_emotion"],
        "songs_playlist": pipeline_data["playlist_result"]["list"],
        "predicted_emotions": pipeline_data["ai_result"]["predicted_emotions"],
        "predictions_list": pipeline_data["ai_result"]["predictions_list"],
        "others_prediction": pipeline_data["ai_result"]["others_probability"],
    }

    # ✅ Cache final result for idempotency + polling + websocket
    # redis.setex(
    #     f"playlist:result:{pipeline_data['request_id']}",
    #     1800,
    #     json.dumps({"status": "SUCCESS", "result": final_result}),
    # )

    signature(
        "db.save_new_playlist",
        args=(pipeline_data,),
    ).apply_async()  # fire-and-forget db save for faster response to client (non-blocking)

    return final_result