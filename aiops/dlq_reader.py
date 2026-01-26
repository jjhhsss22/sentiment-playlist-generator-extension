import redis
import time

DLQ_REDIS_URL = "redis://localhost:6379/2"
redis_dlq = redis.Redis.from_url(DLQ_REDIS_URL, decode_responses=True)

def read_recent_dlq_entries(since_seconds=300):
    """
    Read DLQ entries since the last N seconds.
    """
    now = time.time()
    min_ts = now - since_seconds

    keys = redis_dlq.zrangebyscore(
        "dlq:index",
        min_ts,
        now
    )

    entries = []
    for key in keys:
        data = redis_dlq.hgetall(key)
        if not data:
            continue

        entries.append({
            "dlq_key": key,
            "task": data.get("task_name"),
            "error_type": data.get("error_type"),
            "count": int(data.get("count", 0)),
            "first_seen": float(data.get("first_seen", 0)),
            "last_seen": float(data.get("last_seen", 0)),
            "retries": int(data.get("retries", 0)),
        })

    return entries