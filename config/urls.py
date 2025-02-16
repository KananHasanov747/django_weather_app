from django.conf import settings
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path("", include("server.urls")),  # 'api/'
    path("", include("users.urls")),
    path("", include("client.urls")),
]

if not settings.TESTING:
    try:
        from debug_toolbar.toolbar import debug_toolbar_urls

        urlpatterns = [
            *urlpatterns,
        ] + debug_toolbar_urls()
    except ImportError:
        pass
