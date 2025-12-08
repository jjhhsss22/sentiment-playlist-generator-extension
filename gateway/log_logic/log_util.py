from flask import request, current_app, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def log(level, event, **extra_kwargs):
    """
    Standardised JSON production logs.
    """

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