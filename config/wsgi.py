"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import logging

from django.core.wsgi import get_wsgi_application

from django.conf import settings

# Set up logging early in the application lifecycle
logger = logging.getLogger(__name__)

if settings.DEBUG:
    logger.info("Django Debug mode is ENABLED.")
else:
    logger.info("Django Debug mode is DISABLED.")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
