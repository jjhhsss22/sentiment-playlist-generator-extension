from flask import g, has_request_context
import logging
import sys
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def __init__(self, service_name):
        super().__init__()
        self.service_name = service_name

    def format(self, record):
        log = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(record, "request_id", None),
            "service": self.service_name,
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        return json.dumps(log)

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(g, "request_id", None)
        else:
            record.request_id = None
        return True

def configure_logging(service_name: str = "auth"):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # stdout for normal logs
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(JsonFormatter(service_name))
    stdout_handler.addFilter(RequestIdFilter())

    # stderr for errors
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(JsonFormatter(service_name))
    stderr_handler.addFilter(RequestIdFilter())

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    logger.propagate = False  # prevent duplicate logs
