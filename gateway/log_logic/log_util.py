from flask import request, current_app
from flask_jwt_extended import get_jwt_identity

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
            "user_id": int(get_jwt_identity()),
            "ip": request.remote_addr,
            **extra_kwargs
        }
    )