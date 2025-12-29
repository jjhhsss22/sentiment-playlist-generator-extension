from celery import Celery, signature
import os
import sys
from log_logic.log_util import task_log

# sys.path.append("/app")  # for docker

# redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_url = "redis://localhost:6379/0"

celery = Celery(
    "music",
    broker=redis_url,
    backend=redis_url,
)

celery.conf.task_routes = {
    "music.*": {"queue": "music"}
}

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=True,
)

@celery.task(
    name="music.generate_playlist",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_jitter=True,
)
def generate_playlist(self, pipeline_data):
    self.update_state(
        state="PROGRESS",
        meta={"step": "Generating personalised playlist..."}
    )

    try:
        from music_logic.music_module import generate_playlist_pipeline

        playlist = generate_playlist_pipeline(
            pipeline_data["ai_result"]["starting_coord"],
            pipeline_data["ai_result"]["target_coord"]
        )

        pipeline_data.update({
            "playlist_result": playlist,
        })
    except Exception as e:
        raise

    signature(
        "db.save_new_playlist",
        args=(pipeline_data,),
    ).apply_async()  # fire-and-forget db save for faster response to client (non-blocking)

    return {
        "success": True,
        "message": "Playlist generated successfully!",
        "desired_emotion": pipeline_data["ai_result"]["desired_emotion"],
        "songs_playlist": pipeline_data["playlist_result"]["list"],
        "predicted_emotions": pipeline_data["ai_result"]["predicted_emotions"],
        "predictions_list": pipeline_data["ai_result"]["predictions_list"],
        "others_prediction": pipeline_data["ai_result"]["others_probability"]
    }