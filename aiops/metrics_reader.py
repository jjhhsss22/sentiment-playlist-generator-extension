import redis
import time
import os

METRICS_REDIS_URL = os.environ.get("METRICS_REDIS_URL", "redis://redis:6379/3")
redis_metrics = redis.Redis.from_url(METRICS_REDIS_URL, decode_responses=True)


def _current_window():
    return str(int(time.time() // 60))


def _previous_window():
    """get the previous completed window to avoid race conditions"""
    current = int(time.time() // 60)
    return str(current - 1)


def read_task_metrics(task: str, use_previous_window=True):
    """
    read task metrics from Redis.

    args:
        task: Task name
        use_previous_window: If True, read from previous complete window (recommended)
    """
    window = _previous_window() if use_previous_window else _current_window()

    def get(metric):
        return int(redis_metrics.get(f"metrics:{task}:{metric}:{window}") or 0)

    # calculate percentiles from sorted set
    lat_key = f"latencies:{task}:{window}"
    percentiles = _calculate_percentiles(lat_key)

    return {
        "success": get("success"),
        "errors": get("errors"),
        "retries": get("retries"),
        "latency_sum": get("latency_sum"),
        "latency_count": get("latency_count"),
        "latency_max": get("latency_max"),
        "latency_p50": percentiles["p50"],
        "latency_p95": percentiles["p95"],
        "latency_p99": percentiles["p99"],
    }


def _calculate_percentiles(lat_key: str) -> dict:
    """calculate p50, p95, p99 from sorted set"""

    latencies = redis_metrics.zrange(lat_key, 0, -1, withscores=True)

    if not latencies:
        return {"p50": 0, "p95": 0, "p99": 0}

    # extract scores and sort
    values = sorted([int(score) for _, score in latencies])
    n = len(values)

    def percentile(p):
        if n == 0:
            return 0
        k = int(n * p)
        return values[min(k, n - 1)]

    return {
        "p50": percentile(0.50),
        "p95": percentile(0.95),
        "p99": percentile(0.99),
    }


def list_tasks():
    keys = redis_metrics.keys("metrics:*:success:*")
    return list({k.split(":")[1] for k in keys})