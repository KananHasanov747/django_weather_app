import environ

env = environ.Env(DJANGO_ENVIRONMENT=(str, "development"))

if env("DJANGO_ENVIRONMENT") == "production":
    from .production import *  # noqa
elif env("DJANGO_ENVIRONMENT") == "staging":
    from .staging import *  # noqa
else:
    from .development import *  # noqa
