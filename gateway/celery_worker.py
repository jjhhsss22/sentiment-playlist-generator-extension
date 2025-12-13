from celery import Celery
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

@celery.task(name="gateway.full_playlist_generation_pipeline")
def generate_playlist_pipeline(text, desired_emotion, user_id, request_id):

    workflow = chain(
        celery.signature(
            "ai.predict_emotion",
            args=(text, desired_emotion, user_id, request_id)
        ),
        celery.signature("music.generate_playlist"),
        celery.signature("db.save_new_playlist"),
    )  # chain = output of previous celery task --> input of next celery task

    result = workflow.apply_async()
    return {
        "id": result.id
        }