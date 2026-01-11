from celery import Celery
from celery.exceptions import Ignore
import os
import sys
import redis
import json
import time
import tensorflow as tf
from tensorflow.errors import InvalidArgumentError
from requests.exceptions import Timeout, ConnectionError
from json import JSONDecodeError

from log_logic.log_util import task_log

sys.path.append("/app")  # for docker

CELERY_REDIS_URL = os.environ.get("CELERY_REDIS_URL", "redis://localhost:6379/0")
CACHE_REDIS_URL = "redis://localhost:6379/1"

celery = Celery(
    "ai",
    broker=CELERY_REDIS_URL,
    backend=CELERY_REDIS_URL,
)

celery.conf.task_routes = {
    "ai.*": {"queue": "ai"}
}

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Seoul",
    enable_utc=True,
)

redis_cache = redis.Redis.from_url(CACHE_REDIS_URL, decode_responses=True)

# Load model once at import time (relative to the CWD)
sentiment_model = tf.keras.models.load_model("model/sentiment_model3.keras", compile=False)

sentiment_model.compile(optimizer="adam",
                            loss="categorical_crossentropy",
                            metrics=["accuracy"])



@celery.task(
    name="ai.predict_emotion",
    bind=True,
    autoretry_for=(Timeout, ConnectionError),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,  # retries wait longer each time (exponential)
    retry_jitter=True,  # retries randomly staggered
)
def run_prediction_task(self, pipeline_data):

    try:
        start = time.monotonic()

        self.update_state(
            state="PROGRESS",
            meta={"step": "Generating emotion prediction..."},
        )

        redis_cache.publish(
            "playlist:progress",
            json.dumps({
                "request_id": pipeline_data["request_id"],
                "step": "Generating emotion prediction...",
                "task": self.name,
            })
        )

        from deployment.ai_module import run_prediction_pipeline
        result = run_prediction_pipeline(
            sentiment_model,
            pipeline_data["text"],
            pipeline_data["desired_emotion"]
        )

        pipeline_data.update({
            "ai_result": result,
        })

        duration_ms = int((time.monotonic() - start) * 1000)

        task_log(
            20,
            "ai_emotion_prediction.completed",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            predicted_emotions=result["predicted_emotions"],
            duration_ms=duration_ms,
        )

        return pipeline_data

    except InvalidArgumentError:
        self.update_state(
            state="FAILURE",
            meta={"success": False,
                  "message": "Invalid input. Please type in full sentences"}
        )
        raise Ignore()

    except (KeyError, TypeError, JSONDecodeError) as e:
        task_log(
            40,
            "pipeline_data_error",
            request_id=pipeline_data.get("request_id"),
            user_id=pipeline_data.get("user_id"),
            task_id=self.request.id,
            error = f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )
        raise

    except (Timeout, ConnectionError) as e:
        task_log(
            40,
            "infra_failure_retrying",
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
            "unhandled_exception",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            error = f"{e.__class__.__name__}: {str(e) or 'no message'}",
        )
        raise Ignore()

# celery -A celery_worker:celery worker -l INFO -P solo