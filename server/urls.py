from django.urls import path

from server import views


urlpatterns = [
    path("api/", views.api.urls),
    path("search/<str:query>/", views.city_search_view, name="city_search"),
]
