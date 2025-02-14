from ._base import *

DEBUG = True

INSTALLED_APPS.insert(
    INSTALLED_APPS.index("django.contrib.staticfiles"), "servestatic.runserver_nostatic"
)
INSTALLED_APPS += ["django_browser_reload", *PROJECT_APPS]

ALLOWED_HOSTS = ["localhost", "weather.com"]

CSRF_TRUSTED_ORIGINS = ["https://weather.com", "http://weather.com"]

MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

# ServeStatic (ASGI-versioned WhiteNoise)

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware"),
    "config.middleware.CustomServeStaticMiddleware",
)


STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "config.storage.CompressedManifestStaticFilesStorage",
    },
}

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
