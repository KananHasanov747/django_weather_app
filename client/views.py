from asgiref.sync import sync_to_async
from loguru import logger

from django.shortcuts import render
from django.http import HttpResponse

from config.utils import get_location
from server.views import weather_view


# path('', views.index_view, name="index")
async def index_view(request) -> HttpResponse:
    logger.bind(view="index_view")

    logger.info("GET request to render index view")
    try:
        location = await sync_to_async(get_location)(request)

        # FIX: remove query request support (or update it): ?city=Baku&country=Azerbaijan
        data = await weather_view(
            request,
            city=request.GET.get(
                "city",
                request.COOKIES.get(
                    "city", None
                )  # Return if a user visited a city & reloaded the page
                or location.get("city", None)
                or "Tokyo",
            ),
            country=request.GET.get(
                "country",
                request.COOKIES.get("country", None)
                or location.get("country", None)
                or "Japan",
            ),
            lat=request.GET.get(
                "lat",
                request.COOKIES.get("lat", None)
                or location.get("lat", None)
                or "35.68970000000000197",
            ),
            lon=request.GET.get(
                "lon",
                request.COOKIES.get("lon", None)
                or location.get("lon", None)
                or "139.692200000000014",
            ),
        )

        template_name = "components/weather.html" if request.htmx else "index.html"

        return await sync_to_async(render, thread_sensitive=False)(
            request, template_name, {"data": data, "weather_action": True}
        )
    except Exception as e:
        logger.exception(f"Error during index_view processing: {e}")
        return HttpResponse("<h1>Internal Server Error</h1>", status=500)
