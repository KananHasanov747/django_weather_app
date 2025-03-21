import environ
import multiprocessing
from uvicorn.workers import UvicornWorker

from config.logging_config import GunicornLogger

env = environ.Env(
    DJANGO_HOST=(str, "0.0.0.0"),
    DJANGO_PORT=(str, "8000"),
    DJANGO_UDS=(str, ""),
    DJANGO_SSL_CERTFILE=(str, ""),
    DJANGO_SSL_KEYFILE=(str, ""),
    DJANGO_LOG_LEVEL=(str, "INFO"),
    DJANGO_GUNICORN_DAEMON=(bool, False),
)

bind = env("DJANGO_UDS") or f'{env("DJANGO_HOST")}:{env("DJANGO_PORT")}'
if env("DJANGO_SSL"):
    certfile = env("DJANGO_SSL_CERTFILE")
    keyfile = env("DJANGO_SSL_KEYFILE")
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = UvicornWorker
dameon = env("DJANGO_GUNICORN_DAEMON")
timeout = 600
loglevel = str(env("DJANGO_LOG_LEVEL")).lower()
logger_class = GunicornLogger
