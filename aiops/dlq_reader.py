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
        if data:
            entries.append(data)

    return entries