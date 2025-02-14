from django.apps import AppConfig


class ClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "client"

    def ready(self):
        from . import logging as app_logging

        app_logging.setup_views()
