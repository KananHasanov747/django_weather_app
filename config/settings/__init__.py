import os
import environ

env = environ.Env(DJANGO_ENVIRONMENT=(str, "development"))

if env("DJANGO_ENVIRONMENT") == "production":
    environ.Env.read_env(".env.prod")
    from .production import *
elif env("DJANGO_ENVIRONMENT") == "staging":
    environ.Env.read_env(".env.staging")
    from .staging import *
else:
    environ.Env.read_env(".env.dev")
    from .development import *
