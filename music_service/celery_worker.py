from celery import Celery
import redis
import json
import time
from celery.exceptions import Ignore
from requests.exceptions import Timeout, ConnectionError

from log_logic.log_util import task_log

# sys.path.append("/app")  # for docker

# redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_REDIS_URL = "redis://localhost:6379/0"
CACHE_REDIS_URL = "redis://localhost:6379/1"

celery = Celery(
    "music",
    broker=CELERY_REDIS_URL,
    backend=CELERY_REDIS_URL,
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

redis_cache = redis.Redis.from_url(CACHE_REDIS_URL, decode_responses=True)

@celery.task(
    name="music.generate_playlist",
    bind=True,
    autoretry_for=(Timeout, ConnectionError),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_jitter=True,
)
def generate_playlist(self, pipeline_data):

    try:
        start = time.monotonic()

        self.update_state(
            state="PROGRESS",
            meta={"step": "Generating personalised playlist..."}
        )

        redis_cache.publish(
            "playlist:progress",
            json.dumps({
                "request_id": pipeline_data["request_id"],
                "step": "Generating personalised playlist...",
                "task": self.name,
            })
        )

        from music_logic.music_module import generate_playlist_pipeline

        playlist = generate_playlist_pipeline(
            pipeline_data["ai_result"]["starting_coord"],
            pipeline_data["ai_result"]["target_coord"]
        )

        pipeline_data.update({
            "playlist_result": playlist,
        })

        duration_ms = int((time.monotonic() - start) * 1000)

        task_log(
            20,
            "music.playlist_generation.completed",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            playlist_length=len(playlist["list"]),
            duration_ms=duration_ms,
        )

        return pipeline_data

    except (Timeout, ConnectionError) as e:
        task_log(
            30,
            "music.playlist_generation.retry",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            error = f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )
        raise

    except Exception as e:
        task_log(
            50,
            "music.playlist_generation.failure",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            error = f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )
        raise Ignore()

