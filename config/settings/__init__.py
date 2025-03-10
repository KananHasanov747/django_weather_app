import environ

env = environ.Env(DJANGO_ENVIRONMENT=(str, "development"))

if env("DJANGO_ENVIRONMENT") == "production":
    from .production import *
elif env("DJANGO_ENVIRONMENT") == "staging":
    from .staging import *
else:
    from .development import *
