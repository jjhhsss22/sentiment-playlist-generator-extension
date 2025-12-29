from celery import Celery, signature
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



@celery.task(
    name="db.save_new_playlist",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2},
    retry_backoff=True,
    retry_jitter=True,
)
def save_new_playlist(self, pipeline_data):

    self.update_state(
        state="PROGRESS",
        meta={"step": "Saving playlist..."}
    )

    try:
        from db_structure.db_module import create_playlist, save

        playlist = create_playlist(
            pipeline_data["text"],
            pipeline_data["ai_result"]["likely_emotion"],
            pipeline_data["desired_emotion"],
            pipeline_data["playlist_result"]["text"],
            pipeline_data["user_id"],
        )
        save(playlist)

    except Exception as e:
        signature(
            "db.dlq.save_failed_playlist",
            args=(pipeline_data, str(e)),
        ).apply_async()
        raise


@celery.task(name="db.dlq.save_failed_playlist")
def handle_failed_playlist(pipeline_data, error_message):
    pass  # can save failed playlist data in another table for example and retry