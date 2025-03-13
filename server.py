import os
import uvicorn
import environ

if __name__ == "__main__":
    if "DJANGO_ENVIRONMENT" not in os.environ:
        raise ValueError("DJANGO_ENVIRONMENT must be set")

    env = environ.Env(
        DJANGO_PORT=(int, 443),
        DJANGO_HOST=(str, "0.0.0.0"),
        DJANGO_SSL=(bool, False),
        DJANGO_ENV_NAME=(str, ""),
    )
    environ.Env.read_env(env("DJANGO_ENV_NAME"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.conf import settings
    from config.logging import django_logger, UVICORN_LOGGING_CONFIG

    kwargs = {
        "host": env("DJANGO_HOST"),  # Bind to all interfaces
        "port": env("DJANGO_PORT"),
        "log_config": UVICORN_LOGGING_CONFIG,
        "log_level": "debug" if settings.DEBUG else "info",
        **(
            {
                "reload": True,  # Auto-reload in development
                "reload_dirs": [settings.BASE_DIR],
                "reload_includes": ["*.py", "*.html", "*.js", "*.css"],
            }
            if settings.DEBUG
            else {
                # "workers": 4,  # Number of worker processes
            }
        ),
        **(
            {
                "ssl_keyfile": env("DJANGO_SSL_KEYFILE"),
                "ssl_certfile": env("DJANGO_SSL_CERTFILE"),
            }
            if env("DJANGO_SSL")
            else {}
        ),
        "timeout_keep_alive": 30,
        "access_log": True,
    }

    django_logger.info("Starting Uvicorn server")
    uvicorn.run("config.asgi:application", **kwargs)
