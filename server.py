import os
import uvicorn
import environ

from django.conf import settings

env = environ.Env(
    DJANGO_PORT=(int, 443), DJANGO_HOST=(str, "0.0.0.0"), DJANGO_SSL=(bool, False)
)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    kwargs = {
        "host": env("DJANGO_HOST"),  # Bind to all interfaces
        "port": env("DJANGO_PORT"),
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
    }

    uvicorn.run("config.asgi:application", **kwargs)
