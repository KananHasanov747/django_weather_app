import os
from dotenv import load_dotenv

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from debug_toolbar.toolbar import debug_toolbar_urls

load_dotenv()

urlpatterns = [
    path("admin/" if settings.DEBUG else f'{os.getenv("ADMIN_URL")}/', admin.site.urls),
    path("", include("server.urls")),  # 'api/'
    path("", include("users.urls")),
    path("", include("client.urls")),
]

# Django debug toolbar
if not settings.TESTING:
    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()
