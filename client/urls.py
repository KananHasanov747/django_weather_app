from django.urls import path

from client import views

app_name = "client"
urlpatterns = [
    path("", views.index_view, name="index")
    # re_path(r"^(?P<city>\w+)/(?P<country>\w+)/", views.index_view, name="index"),
]
