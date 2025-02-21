import os
from django.conf import settings

from django.urls import path

from server import views


urlpatterns = [
    path(
        "api/" if settings.DEBUG else f"{os.getenv("DJANGO_API_URL")}/", views.api.urls
    ),
    path("search/<str:query>/", views.city_search_view, name="city_search"),
]
