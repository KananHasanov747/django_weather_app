from django.urls import path

from users import views

app_name = "users"
urlpatterns = [
    path("accounts/<str:action>/", views.auth_view, name="auth"),
]
