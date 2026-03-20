import time
import redis
import os

METRICS_REDIS_URL = os.environ.get("METRICS_REDIS_URL", "redis://redis:6379/3")
redis_metrics = redis.Redis.from_url(METRICS_REDIS_URL, decode_responses=True)

# private helpers

def _bucket(minutes: int = 1) -> str:
    """
    returns time bucket for aggregation
    default: per-minute bucket
    """
    return str(int(time.time() // (60 * minutes)))


def _key(task: str, metric: str, window: str) -> str:
    """
    returns the redis key for a metric and window combination
    """

    return f"metrics:{task}:{metric}:{window}"


# public

LATENCY_MAX_LUA = """
    local key = KEYS[1]
    local value = tonumber(ARGV[1])

    local current = redis.call("GET", key)
    if not current or tonumber(current) < value then
        redis.call("SET", key, value)
    end
    """


def record_latency(task: str, duration_ms: int):
    """
    record task latency
    increments sum & count and finds max latency via lua script so that p95 can be estimated later
    """
    window = _bucket()

    sum_key = _key(task, "latency_sum", window)
    count_key = _key(task, "latency_count", window)
    max_key = _key(task, "latency_max", window)

    pipe = redis_metrics.pipeline()
    pipe.incrby(sum_key, duration_ms)
    pipe.incr(count_key)
    pipe.expire(sum_key, 3600)
    pipe.expire(count_key, 3600)
    pipe.execute()

    # max lua script cannot be pipelined
    redis_metrics.eval(
        LATENCY_MAX_LUA,
        1,
        max_key,
        duration_ms,
    )

    redis_metrics.expire(max_key, 3600)

    lat_key = f"latencies:{task}:{window}"
    redis_metrics.zadd(lat_key, {str(time.time()): duration_ms})
    redis_metrics.zremrangebyrank(lat_key, 0, -10001)  # keep last 10k
    redis_metrics.expire(lat_key, 3600)


def record_error(task: str):
    """
    increment error counter
    """
    window = _bucket()

    error_key = _key(task, "errors", window)

    redis_metrics.incr(error_key)
    redis_metrics.expire(error_key, 3600)


def record_retry(task: str):
    """
    increment retry counter
    """
    window = _bucket()

    retry_key = _key(task, "retries", window)

    redis_metrics.incr(retry_key)
    redis_metrics.expire(retry_key, 3600)


def record_success(task: str):
    """
    increment success counter (throughput)
    """
    window = _bucket()

    success_key = _key(task, "success", window)

    redis_metrics.incr(success_key)
    redis_metrics.expire(success_key, 3600)