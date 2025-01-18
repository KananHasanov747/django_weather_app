from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from server.views import weather_view


# path('', views.index_view, name="index")
@login_required
async def index_view(request):
    request_get = request.GET.get
    data = await weather_view(
        request,
        city=request_get("city", "Tokyo"),
        country=request_get("country", "Japan"),
    )

    # print(f"request.htmx={bool(request.htmx)}")
    template_name = "components/weather.html" if request.htmx else "index.html"
    return render(request, template_name, {"data": data})
