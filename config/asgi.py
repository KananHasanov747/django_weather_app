"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

# import logging

from loguru import logger

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

from django.conf import settings

logger.info(f"Django Debug mode is {'ENABLED' if settings.DEBUG else 'DISABLED'}")

# Set up logging early in the application lifecycle
# logger = logging.getLogger(__name__)

# if settings.DEBUG:
#     logger.info("Django Debug mode is ENABLED.")
# else:
#     logger.info("Django Debug mode is DISABLED.")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings._base")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
    }
)
