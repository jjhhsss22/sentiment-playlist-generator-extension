from celery import Celery
from celery.exceptions import Ignore
import os
import sys
import tensorflow as tf
from tensorflow.errors import InvalidArgumentError

from log_logic.log_util import task_log

sys.path.append("/app")  # for docker

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "ai",
    broker=redis_url,
    backend=redis_url,
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

# Load model once at import time (relative to the CWD)
sentiment_model = tf.keras.models.load_model("model/sentiment_model3.keras", compile=False)

sentiment_model.compile(optimizer="adam",
                            loss="categorical_crossentropy",
                            metrics=["accuracy"])



@celery.task(
    name="ai.predict_emotion",
    bind=True,
    autoretry_for=[Exception,],  # TODO - make this more narrow
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,  # retries wait longer each time (exponential)
    retry_jitter=True,  # retries randomly staggered
)
def run_prediction_task(self, pipeline_data):

    self.update_state(
        state="PROGRESS",
        meta={"step": "Generating emotion prediction..."},
    )

    try:
        from deployment.ai_module import run_prediction_pipeline
        result = run_prediction_pipeline(
            sentiment_model,
            pipeline_data["text"],
            pipeline_data["desired_emotion"]
        )

        pipeline_data.update({
            "ai_result": result,
        })

        return pipeline_data

    except InvalidArgumentError:
        self.update_state(
            state="FAILURE",
            meta={"success": False,
                  "message": "Invalid input. Please type in full sentences"}
        )
        raise Ignore()

    except Exception as e:
        task_log(
            50,
            "celery task failure",
            request_id=pipeline_data["request_id"],
            user_id=pipeline_data["user_id"],
            task_id=self.request.id,
            error=f"{e.__class__.__name__}: {str(e)}"
        )
        raise

# celery -A celery_worker:celery worker -l INFO -P solo