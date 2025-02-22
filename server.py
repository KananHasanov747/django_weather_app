import uvicorn
import environ

from django.conf import settings

env = environ.Env(DJANGO_PORT=(int, 443))

if __name__ == "__main__":
    kwargs = {
        "host": "0.0.0.0",  # Bind to all interfaces
        "port": env("DJANGO_PORT"),
        **(
            {
                "reload": True,  # Auto-reload in development
                "reload_dirs": [settings.BASE_DIR],
                "reload_includes": ["*.py", "*.html", "*.js", "*.css"],
            }
            if settings.DEBUG
            else {
                "workers": 4,  # Number of worker processes
            }
        ),
        "ssl_keyfile": env("DJANGO_SSL_KEYFILE"),
        "ssl_certfile": env("DJANGO_SSL_CERTFILE"),
        "timeout_keep_alive": 30,
    }

    uvicorn.run("config.asgi:application", **kwargs)
