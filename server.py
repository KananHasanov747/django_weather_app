import os
import asyncio
import uvicorn
import environ


async def run():
    if "DJANGO_ENVIRONMENT" not in os.environ:
        raise ValueError("DJANGO_ENVIRONMENT must be set")

    env = environ.Env(  # Default value will only work if not in os.environ
        DJANGO_HOST=(str, "0.0.0.0"),
        DJANGO_PORT=(int, 443),
        DJANGO_UDS=(str, ""),
        DJANGO_SSL=(bool, False),
    )
    environ.Env.read_env()

    from loguru import logger
    from aiocache import Cache
    from django.conf import settings
    from config.logging_config import UVICORN_LOGGING_CONFIG

    cache = Cache(Cache.REDIS, endpoint="127.0.0.1", port=6379, namespace="main")
    await cache.delete("key")

    kwargs = {
        **(
            {
                "host": env("DJANGO_HOST"),
                "port": env("DJANGO_PORT"),
            }
            if not env("DJANGO_UDS")
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

    logger.info("Starting Uvicorn server")
    uvicorn.run("config.asgi:application", **kwargs)


if __name__ == "__main__":
    asyncio.run(run())
