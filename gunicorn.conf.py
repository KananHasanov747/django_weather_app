import environ
import multiprocessing
from uvicorn.workers import UvicornWorker

env = environ.Env(
    DJANGO_HOST=(str, "0.0.0.0"),
    DJANGO_PORT=(str, "8000"),
    DJANGO_SSL_CERTFILE=(str, ""),
    DJANGO_SSL_KEYFILE=(str, ""),
    DJANGO_GUNICORN_DAEMON=(bool, False),
)

bind = f'{env("DJANGO_HOST")}:{env("DJANGO_PORT")}'
certfile = env("DJANGO_SSL_CERTFILE")
keyfile = env("DJANGO_SSL_KEYFILE")
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = UvicornWorker
dameon = env("DJANGO_GUNICORN_DAEMON")
timeout = 600
