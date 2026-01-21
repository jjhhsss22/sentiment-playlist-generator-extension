import json
import time

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

    service="gateway"
    ts = time.time()
    window = int(ts // 60)

    dlq_key = f"dlq:{service}:task:{task.request.id}"
    payload_key = f"dlq:{service}:payload:{request_id}"

    redis_dlq.hset(
        dlq_key,
        mapping={
            "service": service,
            "task_name": task.name,
            "task_id": task.request.id,
            "request_id": request_id,
            "user_id": user_id or "",
            "error_type": exc.__class__.__name__,
            "error_message": str(exc) or "no message",
            "retries": task.request.retries,
            "timestamp": ts,
            "window": window,
        }
    )

    # index for analytics
    redis_dlq.zadd("dlq:index", {dlq_key: ts})

    # store payload separately with TTL
    if payload is not None:
        redis_dlq.setex(
            payload_key,
            86400,  # 24h
            json.dumps(payload)
        )