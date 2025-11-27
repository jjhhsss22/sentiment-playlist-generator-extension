from flask import request, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def log(level, event, **extra_kwargs):

    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id is not None:
            user_id = int(user_id)
    except Exception:
        pass

    current_app.logger.log(
        level,  # level - INFO 20, WARNING 30, ERROR 40, CRITICAL 50
        {
            "event": event,
            "path": request.path,
            "method": request.method,
            "user_id": user_id,
            "ip": request.remote_addr,
            **extra_kwargs
        }
    )