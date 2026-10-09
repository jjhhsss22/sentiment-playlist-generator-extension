from flask import request, g
import logging

def log(level, event, **extra_kwargs):
    """
    Standardised JSON production logs.
    """

    logging.getLogger("gateway.http").log(
        level,  # level - INFO 20, WARNING 30, ERROR 40, CRITICAL 50
        {
            "event": event,
            "path": request.path,
            "method": request.method,
            "user_id": getattr(g, "user_id", None),
            "ip": request.remote_addr,
            **extra_kwargs
        }
    )

def task_log(level, event, request_id=None, user_id=None, task_id=None, **extra_kwargs):
    """
    Logging utility for Celery tasks.
    No Flask, no request, no JWT.
    """

    logging.getLogger("gateway.celery").log(
        level,
        {
            "event": event,
            "layer": "celery",
            "request_id": request_id,
            "user_id": user_id,
            "task_id": task_id,
            **extra_kwargs
        }
    )


def redis_log(level, event, request_id=None, **extra_kwargs):
    """
    Logging utility for Redis listeners / pubsub consumers.
    No Flask context, no Celery task context.
    """

    logging.getLogger("gateway.redis").log(
        level,
        {
            "event": event,
            "layer": "redis_listener",
            "request_id": request_id,
            **extra_kwargs,
        }
    )