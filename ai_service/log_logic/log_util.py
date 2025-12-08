from flask import request, current_app, g
import logging

def log(level, event, **extra_kwargs):

    current_app.logger.log(
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

def task_log(level, event, task_id=None, **extra_kwargs):
    """
    Logging utility for Celery tasks.
    No Flask, no request, no JWT.
    """

    logging.getLogger().log(
        level,
        {
            "event": event,
            "user_id": getattr(g, "user_id", None),
            "task_id": task_id,
            **extra_kwargs
        }
    )