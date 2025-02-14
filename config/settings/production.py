from ._base import *

DEBUG = False

INSTALLED_APPS.extend(PROJECT_APPS)

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False
SECURE_CONTENT_TYPE_NOSNIFF = True


# ServeStatic (ASGI-versioned WhiteNoise)

if not env("NGINX_ENABLED"):
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


# ServeStatic cache policy
SERVESTATIC_MAX_AGE = 31536000  # 1 year
