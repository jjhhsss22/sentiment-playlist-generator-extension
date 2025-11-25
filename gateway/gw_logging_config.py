import logging
import sys
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        return json.dumps(log)

def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # stdout for normal logs
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(JsonFormatter())

    # stderr for errors
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(JsonFormatter())

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)