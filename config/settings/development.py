from ._base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost"]

INSTALLED_APPS.insert(
    INSTALLED_APPS.index("django.contrib.staticfiles"), "whitenoise.runserver_nostatic"
)

INSTALLED_APPS += PROJECT_APPS


# Django debug toolbar

if not TESTING:
    INSTALLED_APPS = [
        *INSTALLED_APPS,
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        *MIDDLEWARE,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]


# Whitenoise cache policy
WHITENOISE_MAX_AGE = 31536000 if not DEBUG else 0  # 1 year
