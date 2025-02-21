import uvicorn
import environ

from django.conf import settings

env = environ.Env(DJANGO_PORT=(int, 443))

if __name__ == "__main__":
    uvicorn.run(
        "config.asgi:application",
        host="0.0.0.0",  # Bind to all interfaces
        port=env("DJANGO_PORT"),
        reload=settings.DEBUG,  # Auto-reload in development
        reload_dirs=[settings.BASE_DIR],
        reload_includes=["*.py", "*.html", "*.js", "*.css"],
        workers=4,  # Number of worker processes
        ssl_keyfile=env("DJANGO_SSL_KEYFILE"),
        ssl_certfile=env("DJANGO_SSL_CERTFILE"),
        timeout_keep_alive=30,
    )
