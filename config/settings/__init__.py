import os
import environ

env = environ.Env(DJANGO_ENVIRONMENT=(str, "development"))

if env("DJANGO_ENVIRONMENT") == "production":
    os.environ.setdefault("DJANGO_ENV_NAME", ".env.prod")
    from .production import *
elif env("DJANGO_ENVIRONMENT") == "staging":
    os.environ.setdefault("DJANGO_ENV_NAME", ".env.staging")
    from .staging import *
else:
    os.environ.setdefault("DJANGO_ENV_NAME", ".env.dev")
    from .development import *
