import json
import time
import hashlib


def _stable_hash(data) -> str:
    """create a stable hash for payload deduplication."""

    if data is not None:
        dumped = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(dumped.encode()).hexdigest()[:12]

    return ""


def push_to_dlq(
        *,
        redis_dlq,
        task,
        request_id,
        user_id=None,
        payload=None,
        exc,
):
    """
    push a failed task to Redis DLQ.

    - metadata stored in a HASH (fast scans, low memory)
    - payload stored separately with TTL (privacy + size control)
    - indexed by timestamp for analytics / cron recovery jobs
    """

    service = "music"
    ts = time.time()
    window = int(ts // 60)

    error_type = exc.__class__.__name__
    payload_hash = _stable_hash(payload)

    # 🔑 Fingerprinted DLQ key (THIS IS THE BIG CHANGE)
    dlq_key = (
        f"dlq:{service}:"
        f"task:{task.name}:"
        f"error:{error_type}:"
        f"payload:{payload_hash}"
    )

    pipe = redis_dlq.pipeline()

    # failure metadata (deduplicated)
    pipe.hsetnx(dlq_key, "service", service)
    pipe.hsetnx(dlq_key, "task_name", task.name)
    pipe.hsetnx(dlq_key, "error_type", error_type)
    pipe.hsetnx(dlq_key, "first_seen", ts)

    pipe.hset(dlq_key, mapping={
        "last_seen": ts,
        "last_request_id": request_id,
        "last_user_id": user_id or "",
        "last_task_id": task.request.id,
        "retries": task.request.retries,
        "window": window,
    })

    pipe.hincrby(dlq_key, "count", 1)  # recurrence counter
    pipe.zadd("dlq:index", {dlq_key: ts})  # index for analytics / cron jobs
    pipe.expire(dlq_key, 7 * 24 * 3600)  # keep DLQ metadata longer

    pipe.execute()

    # payload storage (TEMPORARY)
    if payload is not None:
        payload_key = f"{dlq_key}:payload"

        redis_dlq.setex(
            payload_key,
            24 * 3600,  # 24h only
            json.dumps(payload)
        )