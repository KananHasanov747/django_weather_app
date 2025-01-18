import os
from django.conf import settings
from dotenv import load_dotenv

from django.urls import path

from server import views

load_dotenv()

app_name = "server"

urlpatterns = [
    path("api/" if settings.DEBUG else f"{os.getenv("API_URL")}/", views.api.urls),
    path("search/<str:query>/", views.city_search_view, name="city_search"),
]
