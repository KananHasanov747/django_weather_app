"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from loguru import logger

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

from django.conf import settings

logger.info(f"Django Debug mode is {'ENABLED' if settings.DEBUG else 'DISABLED'}")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings._base")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
    }
)
