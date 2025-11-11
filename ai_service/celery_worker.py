from celery import Celery
import os
import sys
import tensorflow as tf

sys.path.append("/app")  # for docker

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "ai_tasks",
    broker=redis_url,
    backend=redis_url,
)

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



@celery.task
def run_prediction_task(input_text, desired_emotion):
    try:
        from deployment.ai_module import run_prediction_pipeline
        return run_prediction_pipeline(sentiment_model, input_text, desired_emotion)
    except Exception as e:
        return {"success": False, "message": str(e)}

# celery -A celery_worker:celery worker -l INFO -P solo