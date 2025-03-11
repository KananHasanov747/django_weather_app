from asgiref.sync import sync_to_async
from loguru import logger as base_logger
from django_ratelimit.core import is_ratelimited
from django_ratelimit.exceptions import Ratelimited

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from server.views import weather_view

logger = base_logger.bind(name="client.views")


# path('', views.index_view, name="index")
@login_required
async def index_view(request) -> HttpResponse:
    # Check if the request is rate-limited
    if await sync_to_async(is_ratelimited)(
        request,
        fn=index_view,
        key="ip",  # Rate limit based on IP address
        rate="1/s",  # 1 request per second
        method="GET",  # Apply to GET requests
        increment=True,  # Increment the counter
    ):
        # Handle rate limit exceeded
        raise Ratelimited()

    logger.info("Index view")
    data = await weather_view(
        request,
        city=request.GET.get("city", "Tokyo"),
        country=request.GET.get("country", "Japan"),
    )

    template_name = "components/weather.html" if request.htmx else "index.html"

    return await sync_to_async(render, thread_sensitive=False)(
        request, template_name, {"data": data}
    )
