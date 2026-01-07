from flask import request, g
import logging

def log(level, event, **extra_kwargs):

    logging.getLogger("auth.http").log(
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