from celery import Celery
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

@celery.task(name="music.generate_playlist", bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def generate_playlist(self, starting_coord, target_coord, user_id, request_id, ai_result):
    from music_logic.music_module import generate_playlist_pipeline

    result = generate_playlist_pipeline(starting_coord, target_coord)

    return {
        **ai_result,
        "playlist": result
    }