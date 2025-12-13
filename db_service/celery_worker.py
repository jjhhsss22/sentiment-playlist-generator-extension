from celery import Celery
import os
import sys

from log_logic.log_util import task_log

# sys.path.append("/app")  # for docker

# redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_url = "redis://localhost:6379/0"

celery = Celery(
    "db",
    broker=redis_url,
    backend=redis_url,
)

celery.conf.task_routes = {
    "db.*": {"queue": "db"}
}

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=True,
)

from db_structure.db_module import create_playlist, save

@celery.task(name="db.save_new_playlist", bind=True, autoretry_for=[Exception,], retry_kwargs={"max_retries": 2})
def save_new_playlist(self, new_playlist, user_id, request_id, pipeline_data):
    try:
        input_text = new_playlist["input_text"]
        likely_emotion = new_playlist["likely_emotion"]
        desired_emotion = new_playlist["desired_emotion"]
        playlist_text = new_playlist["playlist_text"]
        user_id = user_id
    except Exception as e:
        raise

    try:
        playlist = create_playlist(input_text, likely_emotion, desired_emotion, playlist_text, user_id)
        save(playlist)
    except Exception as e:
        raise

    return {
        pipeline_data
    }
