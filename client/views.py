from loguru import logger as base_logger
from server.views import weather_view

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

logger = base_logger.bind(name="client.views")


# path('', views.index_view, name="index")
@login_required
async def index_view(request):
    logger.info("Index view")
    request_get = request.GET.get
    data = await weather_view(
        request,
        city=request_get("city", "Tokyo"),
        country=request_get("country", "Japan"),
    )

    template_name = "components/weather.html" if request.htmx else "index.html"

    response = render(request, template_name, {"data": data})
    return response
