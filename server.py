import os
import uvicorn
import environ


if __name__ == "__main__":
    if "DJANGO_ENVIRONMENT" not in os.environ:
        raise ValueError("DJANGO_ENVIRONMENT must be set")

    env = environ.Env(
        DJANGO_HOST=(str, "0.0.0.0"),
        DJANGO_PORT=(str, "443"),
        DJANGO_UDS=(str, ""),
        DJANGO_SSL=(bool, False),
        DJANGO_ENV_NAME=(str, ""),
    )
    environ.Env.read_env(env("DJANGO_ENV_NAME"))

    from django.conf import settings
    from config.logging_config import django_logger, UVICORN_LOGGING_CONFIG

    kwargs = {
        **(
            {
                "host": env("DJANGO_HOST"),
                "port": env("DJANGO_PORT"),
            }
            if env("DJANGO_UDS")
            else {
                "uds": env("DJANGO_UDS"),
            }
        ),
        "log_config": UVICORN_LOGGING_CONFIG,
        "log_level": "debug" if settings.DEBUG else "info",
        "use_colors": True,
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
