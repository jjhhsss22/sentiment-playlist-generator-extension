import redis
import time

METRICS_REDIS_URL = "redis://localhost:6379/3"
redis_metrics = redis.Redis.from_url(METRICS_REDIS_URL, decode_responses=True)

def _current_window():
    return str(int(time.time() // 60))

def read_task_metrics(task: str):
    window = _current_window()

    def get(metric):
        return int(redis_metrics.get(f"metrics:{task}:{metric}:{window}") or 0)

    return {
        "success": get("success"),
        "errors": get("errors"),
        "retries": get("retries"),
        "latency_sum": get("latency_sum"),
        "latency_count": get("latency_count"),
        "latency_max": get("latency_max"),
    }

def list_tasks():
    keys = redis_metrics.keys("metrics:*:success:*")
    return list({k.split(":")[1] for k in keys})
