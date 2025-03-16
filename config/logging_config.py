import os
import sys
import inspect
import logging
from typing import Union
from loguru import logger
from django.conf import settings
from gunicorn.glogging import Logger as GunicornLoggerBase

logger.remove()

# https://stackoverflow.com/a/77007723


# A custom stderr handler that can be pickled
# (https://docs.python.org/3/library/logging.handlers.html#streamhandler)
class StderrHandler:
    def write(self, message):
        sys.stderr.write(message)

    def flush(self):
        sys.stderr.flush()


# InterceptHandler to redirect Python's logging to Loguru
class InterceptHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop("stream", sys.stderr)
        super().__init__(*args, **kwargs)

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: Union[str, int]
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# https://github.com/benoitc/gunicorn/blob/master/gunicorn/glogging.py
class GunicornLogger(GunicornLoggerBase):
    def __init__(self, cfg):
        super().__init__(cfg)
        # Replace default handlers with InterceptHandler
        self.error_log.handlers = [InterceptHandler()]
        self.access_log.handlers = [InterceptHandler()]


logger.add(
    StderrHandler(),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - {message}",
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
)

LOG_DIR = os.path.join(settings.BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger.add(
    os.path.join(LOG_DIR, "application.log"),
    rotation="500 MB",
    retention="10 days",
    level="DEBUG" if settings.DEBUG else "INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    colorize=True,
)

logger.add(
    os.path.join(LOG_DIR, "errors.log"),
    level="ERROR",
    rotation="100 MB",
    format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level: <8}</level> | {file} | {line} | {message}",
)


# Uvicorn custom logging config (uses logging syntax)
UVICORN_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {  # Placeholder to stop Uvicorn from breaking
        "default": {"fmt": "", "datefmt": "", "use_colors": None},
        "access": {"fmt": "", "datefmt": "", "use_colors": None},
    },
    "handlers": {
        "default": {
            "class": "config.logging_config.InterceptHandler",
            "level": "INFO",
            "stream": "ext://sys.stderr",  # Use string reference to avoid pickling issues (PEP391)
        },
        "access": {
            "class": "config.logging_config.InterceptHandler",
            "level": "INFO",
            "stream": "ext://sys.stderr",  # Use string reference to avoid pickling issues (PEP391)
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}
