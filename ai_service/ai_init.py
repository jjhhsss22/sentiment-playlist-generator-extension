from flask import Flask
import logging

from log_logic.ais_logging_config import configure_logging


def create_ais():
    configure_logging()

    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.WARNING)

    app = Flask(__name__)

    return app