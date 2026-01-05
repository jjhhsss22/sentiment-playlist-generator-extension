from celery import Celery
from celery.exceptions import Ignore
from requests.exceptions import Timeout, ConnectionError
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
    autoretry_for=(Timeout, ConnectionError),
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

        return pipeline_data

    except (Timeout, ConnectionError) as e:
        task_log(
            30,
            "music.retrying",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            error = f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )
        raise

    except Exception as e:
        is_final_attempt = self.request.retries >= self.max_retries

        task_log(
            40 if not is_final_attempt else 50,
            "music.permanent_failure",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            error = f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )
        raise Ignore()

