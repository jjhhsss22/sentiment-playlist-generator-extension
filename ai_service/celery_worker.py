from celery import Celery
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



@celery.task(name="ai.predict_emotion", bind=True, autoretry_for=[InvalidArgumentError, Exception,], retry_kwargs={"max_retries": 3})
def run_prediction_task(self, input_text, desired_emotion, user_id, request_id):
    try:
        from deployment.ai_module import run_prediction_pipeline
        return run_prediction_pipeline(sentiment_model, input_text, desired_emotion)

    except InvalidArgumentError:
        return {"success": False, "message": "please type in full sentences"}

    except Exception as e:
        task_log(
            50,
            "celery task failure",
            task_id=self.request.id,
            error=f"{e.__class__.__name__}: {str(e)}"
        )
        # return {"success": False, "message": "AI task failed"}
        raise

# celery -A celery_worker:celery worker -l INFO -P solo