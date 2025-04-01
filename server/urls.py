from django.urls import path

from server import views


urlpatterns = [
    path("api/", views.api.urls),
]
