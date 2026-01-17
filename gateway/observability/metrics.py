import time
import redis

SERVICE = "gateway"
METRICS_REDIS_URL = "redis://localhost:6379/3"

redis_metrics = redis.Redis.from_url(METRICS_REDIS_URL, decode_responses=True)

# private helpers

def _bucket(minutes: int = 1) -> str:
    """
    Returns time bucket for aggregation.
    Default: per-minute bucket.
    """
    return str(int(time.time() // (60 * minutes)))


def _key(task: str, metric: str, window: str) -> str:
    """
    Returns the redis key for a metric and window combination.
    """

    return f"metrics:{SERVICE}:{task}:{metric}:{window}"


# public

def record_latency(task: str, duration_ms: int):
    """
    Record task latency.
    increments sum & count so p95 can be estimated later.
    """
    window = _bucket()

    pipe = redis_metrics.pipeline()
    pipe.incrby(_key(task, "latency_sum", window), duration_ms)
    pipe.incr(_key(task, "latency_count", window))
    pipe.expire(_key(task, "latency_sum", window), 3600)
    pipe.expire(_key(task, "latency_count", window), 3600)
    pipe.execute()


def record_error(task: str):
    """
    Increment error counter.
    """
    window = _bucket()

    redis_metrics.incr(_key(task, "errors", window))
    redis_metrics.expire(_key(task, "errors", window), 3600)


def record_retry(task: str):
    """
    Increment retry counter.
    """
    window = _bucket()

    redis_metrics.incr(_key(task, "retries", window))
    redis_metrics.expire(_key(task, "retries", window), 3600)


def record_success(task: str):
    """
    Track successful executions (throughput).
    """
    window = _bucket()

    redis_metrics.incr(_key(task, "success", window))
    redis_metrics.expire(_key(task, "success", window), 3600)