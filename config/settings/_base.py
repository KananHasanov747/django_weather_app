import sys
import environ

from pathlib import Path

# from django.conf import settings

###############
# ENVIRONMENT #
###############

env = environ.Env(  # Default value will only work if not in os.environ
    DJANGO_LOG_LEVEL=(str, "INFO"),
    DJANGO_ALLOWED_HOSTS=(str, ""),
    DJANGO_POSTGRES=(bool, False),
    DJANGO_NGINX=(bool, False),
    DJANGO_REDIS=(bool, False),
    DJANGO_SECRET_KEY_FALLBACKS=(str, ""),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")
SECRET_KEY_FALLBACKS = str(env("DJANGO_SECRET_KEY_FALLBACKS")).split(",")

TESTING = "pytest" in sys.argv

INTERNAL_IPS = [
    "127.0.0.1",
]

ALLOWED_HOSTS = str(env("DJANGO_ALLOWED_HOSTS")).split(",")

AUTH_USER_MODEL = "users.User"

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

##########################
# APPLICATION DEFINITION #
##########################

INSTALLED_APPS = [
    app
    for app in [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # plugins and tools
        # "servestatic.runserver_nostatic" if settings.DEBUG else False,
        "django_htmx",
        "django_cotton",
        "django_recaptcha",
        # apps
        "server.apps.ServerConfig",
        "users.apps.UsersConfig",
        "client.apps.ClientConfig",
    ]
    if app
]

MIDDLEWARE = [
    middleware
    for middleware in [
        "config.middleware.XForwardedForMiddleware",  # use only if REMOTE_ADDR is empty
        "django.middleware.security.SecurityMiddleware",
        (
            "servestatic.middleware.ServeStaticMiddleware"
            if not env("DJANGO_NGINX")
            else False
        ),
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "config.middleware.RestrictDirectAccessMiddleware",
        "django.middleware.gzip.GZipMiddleware",
        "django_htmx.middleware.HtmxMiddleware",  # from 'django-htmx' library
        # "config.middleware.RequestLoggingMiddleware",
    ]
    if middleware
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [  # built-in library (tags and filters) without first calling {% load %} tag
                "config.templatetags.filters",  # custom template filters
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
        },
    },
]

ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"


######################
# DATABASE & CACHING #
######################

# TODO: add the ability to switch between databases (like in CACHES)
DATABASES = {
    "default": (
        {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB"),
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST"),
            "PORT": env("POSTGRES_PORT"),
        }
        if env("DJANGO_POSTGRES")
        else {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "OPTIONS": {
                "init_command": "PRAGMA synchronous=3; PRAGMA cache_size=10000; PRAGMA journal_mode=MEMORY;"
            },
        }
    )
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "database_cache",  # table name
    },
    "redis": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    },
    "memcached": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "127.0.0.1:11211",
    },
}

STORAGES = {
    **(
        {
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "config.storage.CompressedManifestStaticFilesStorage",
            },
        }
        if env("DJANGO_NGINX")
        else {
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "servestatic.storage.CompressedManifestStaticFilesStorage",
            },
        }
    )
}

FIXTURE_DIRS = (BASE_DIR / "fixtures",)


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Django Cotton (https://django-cotton.com/)
COTTON_DIR = "components"

LOGGING_CONFIG = None

####################
# GOOGLE reCAPTCHA #
####################

RECAPTCHA_PUBLIC_KEY = env("DJANGO_RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("DJANGO_RECAPTCHA_PRIVATE_KEY")
