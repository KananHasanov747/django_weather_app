import uvicorn
import environ

from django.conf import settings

env = environ.Env()

if __name__ == "__main__":
    uvicorn.run(
        "config.asgi:application",
        host="0.0.0.0",  # Bind to all interfaces
        port=443,
        reload=settings.DEBUG,  # Auto-reload in development
        workers=4,  # Number of worker processes
        ssl_keyfile=env("DJANGO_SSL_KEYFILE"),
        ssl_certfile=env("DJANGO_SSL_CERTFILE"),
        timeout_keep_alive=30,
    )
