###########
# IMPORTS #
###########

# Python imports
import sys
import environ
from pathlib import Path

# Django imports
from django.conf import settings
from django.core.management.utils import get_random_secret_key

###############
# ENVIRONMENT #
###############

env = environ.Env(  # Default value will only work if not in os.environ
    DJANGO_LOG_LEVEL=(str, "INFO"),
    DJANGO_ALLOWED_HOSTS=(str, ""),
    DJANGO_CSRF_TRUSTED_HOSTS=(str, ""),
    DJANGO_POSTGRES=(bool, False),
    POSTGRES_PORT=(str, "5432"),
    DJANGO_NGINX=(bool, False),
    DJANGO_REDIS_LOCATION=(str, "redis://127.0.0.1:6379"),
    DJANGO_SECRET_KEY_FALLBACKS=(str, get_random_secret_key()),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")
SECRET_KEY_FALLBACKS = str(env("DJANGO_SECRET_KEY_FALLBACKS")).split(",")

TESTING = "pytest" in sys.argv

INTERNAL_IPS = [
    "127.0.0.1",
]

ALLOWED_HOSTS = str(env("DJANGO_ALLOWED_HOSTS")).split(",")

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

ROOT_URLCONF = "config.urls"

ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

########################
# INTERNATIONALIZATION #
########################

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

##################
# Authentication #
##################

AUTH_USER_MODEL = "users.User"

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

######################################
# APPLICATIONS/MIDDLEWARES/TEMPLATES #
######################################

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
        "servestatic.runserver_nostatic" if settings.DEBUG else False,
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
        # "config.middleware.XForwardedForMiddleware",  # https://stackoverflow.com/a/34254843
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
    ]
    if middleware
]

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

############################
# DATABASE/CACHES/STORAGES #
############################

# TODO: add the ability to switch between databases (like in CACHES)
DATABASES = {
    "default": (
        {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DATABASE"),
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
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("DJANGO_REDIS_LOCATION").split(","),
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

################
# STATIC FILES #
################

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

#################
# DJANGO COTTON #
#################

COTTON_DIR = "components"

####################
# GOOGLE reCAPTCHA #
####################

RECAPTCHA_PUBLIC_KEY = env("DJANGO_RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("DJANGO_RECAPTCHA_PRIVATE_KEY")

#################
# MISCELLANEOUS #
#################

LOGGING_CONFIG = None
