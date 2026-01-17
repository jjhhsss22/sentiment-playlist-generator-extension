from celery import Celery, signature
from celery.exceptions import Ignore
from sqlalchemy.exc import IntegrityError
import time
import redis
import os
import sys

from log_logic.log_util import task_log
from observability.metrics import record_latency, record_success, record_error, record_retry

# sys.path.append("/app")  # for docker

# redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_REDIS_URL = "redis://localhost:6379/0"
DLQ_REDIS_URL = "redis://localhost:6379/2"

celery = Celery(
    "db",
    broker=CELERY_REDIS_URL,
    backend=CELERY_REDIS_URL,
)

celery.conf.task_routes = {
    "db.*": {"queue": "db"},
    "db.dlq.*": {"queue": "db_dlq"},  # Dead Letter Queue for failed saves
}

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=True,
)

redis_dlq = redis.Redis.from_url(DLQ_REDIS_URL, decode_responses=True)

@celery.task(
    name="db.save_new_playlist",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
    retry_backoff=True,
    retry_jitter=True,
    retry_exclude=(IntegrityError,),
)
def save_new_playlist(self, pipeline_data):
    start = time.monotonic()

    try:
        self.update_state(
            state="PROGRESS",
            meta={"step": "Saving playlist..."}
        )

        from db_structure.db_module import create_playlist, save

        playlist = create_playlist(
            pipeline_data["text"],
            pipeline_data["ai_result"]["likely_emotion"],
            pipeline_data["desired_emotion"],
            pipeline_data["playlist_result"]["text"],
            pipeline_data["user_id"],
            pipeline_data["request_id"]
        )

        save(playlist)

        duration_ms = int((time.monotonic() - start) * 1000)
        record_success(self.name)
        task_log(
            20,
            "playlist_db_save.completed",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            duration_ms=duration_ms,
        )

    except IntegrityError as e:
        record_error(self.name)
        task_log(
            20,
            "db.playlist_already_exists",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            error=f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )
        raise Ignore()

    except Exception as e:
        is_final_attempt = self.request.retries + 1 >= self.max_retries

        if is_final_attempt:
            signature(
                "db.dlq.save_failed_playlist",
                args=(pipeline_data, f"{e.__class__.__name__}: {str(e) or 'no message'}"),
            ).apply_async()

            record_error(self.name)

        record_retry(self.name)
        task_log(
            40 if not is_final_attempt else 50,
            "db.save_failed.retry" if not is_final_attempt else "db.save_failed.dlq",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            retry=self.request.retries,
            max_retries=self.max_retries,
            error=f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )

        raise

    finally:
        duration_ms = int((time.monotonic() - start) * 1000)
        record_latency(self.name, duration_ms)

@celery.task(name="db.dlq.save_failed_playlist")
def handle_failed_playlist(pipeline_data, error_message):

    # final retry for table save
    # if failed add whole payload to failed playlist table (need to create new table)
    # failed_playlists
    # ---------------
    # id
    # request_id
    # user_id
    # payload_json
    # error_message
    # created_at
    # last_retry_at

    pass