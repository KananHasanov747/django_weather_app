import os
import sys
from loguru import logger
from django.conf import settings

logger.remove()


# A custom stderr handler that can be pickled
class StderrHandler:
    def write(self, message):
        sys.stderr.write(message)

    def flush(self):
        sys.stderr.flush()


# Configure loguru
logger.add(
    StderrHandler(),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
)

# File logging
LOG_DIR = os.path.join(settings.BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger.add(
    os.path.join(LOG_DIR, "application.log"),
    rotation="500 MB",
    retention="10 days",
    level="DEBUG" if settings.DEBUG else "INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

logger.add(
    os.path.join(LOG_DIR, "errors.log"),
    level="ERROR",
    rotation="100 MB",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file} | {line} | {message}",
)

# Create a logger instance to use throughout the project
django_logger = logger

# Uvicorn custom logging config
UVICORN_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s | %(levelname)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s | %(levelname)s | %(client_addr)s - "%(request_line)s" %(status_code)s',
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "stream": "ext://sys.stderr",  # Use string reference to avoid pickling issues
            "formatter": "default",
        },
        "access": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "stream": "ext://sys.stderr",  # Use string reference to avoid pickling issues
            "formatter": "access",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}
