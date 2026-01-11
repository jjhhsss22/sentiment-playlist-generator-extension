from celery import Celery, signature
from celery import chain
import redis
import json
import time
import os
import sys

from log_logic.log_util import task_log

# sys.path.append("/app")  # for docker

# redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_REDIS_URL = "redis://localhost:6379/0"
CACHE_REDIS_URL = "redis://localhost:6379/1"  # in ec2 - redis://redis.internal:6379/1

celery = Celery(
    "gateway",
    broker=CELERY_REDIS_URL,
    backend=CELERY_REDIS_URL,
)

celery.conf.task_routes = {
    "gateway.*": {"queue": "gateway"},
    "ai.*": {"queue": "ai"},
    "music.*": {"queue": "music"},
    "db.*": {"queue": "db"},
}

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=True,
)


redis_cache = redis.Redis.from_url(CACHE_REDIS_URL, decode_responses=True)


@celery.task(name="gateway.full_playlist_generation_pipeline", bind=True)
def generate_playlist_pipeline(self, text, desired_emotion, user_id, request_id):

    try:
        self.update_state(
            state="PROGRESS",
            meta={"step": "Starting playlist generation..."},  # for internal introspection / debugging
        )

        redis_cache.publish(
            "playlist:progress",
            json.dumps({
                "request_id": request_id,
                "step": "Starting generation...",
                "task": self.name,
            })
        )  # progress ui

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

    except Exception as e:
        task_log(
            50,
            "gateway.pipeline.dispatch_failed",
            request_id=request_id,
            user_id=user_id,
            task_id=self.request.id,
            error = f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )
        raise

@celery.task(name="gateway.finalise_playlist", bind=True)
def finalise_playlist(self, pipeline_data):

    try:
        start = time.monotonic()

        final_result = {
            "success": True,
            "message": "Playlist generated successfully!",
            "desired_emotion": pipeline_data["ai_result"]["desired_emotion"],
            "songs_playlist": pipeline_data["playlist_result"]["list"],
            "predicted_emotions": pipeline_data["ai_result"]["predicted_emotions"],
            "predictions_list": pipeline_data["ai_result"]["predictions_list"],
            "others_prediction": pipeline_data["ai_result"]["others_probability"],
        }

        redis_cache.setex(
            f"playlist:result:{pipeline_data['request_id']}",
            3600,
            json.dumps(final_result)
        )

        signature(
            "db.save_new_playlist",
            args=(pipeline_data,),
        ).apply_async()  # fire-and-forget db save for faster response to client (non-blocking)

        redis_cache.publish(  # for subscriber thread for websocket
            "playlist:completed",
            json.dumps({
                "request_id": pipeline_data["request_id"],
                "result": final_result,
            })
        )

        duration_ms = int((time.monotonic() - start) * 1000)

        task_log(
            20,
            "playlist_pipeline.completed",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            playlist_size=len(final_result["songs_playlist"]),
            duration_ms=duration_ms,
        )

        return final_result

    except Exception as e:
        task_log(
            50,
            "gateway.pipeline.finalise_failed",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            error = f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )
        raise