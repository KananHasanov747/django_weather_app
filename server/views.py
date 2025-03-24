from loguru import logger
from typing import Dict, List, Optional
from aiocache import cached, RedisCache
from aiocache.serializers import PickleSerializer
from channels.db import database_sync_to_async, sync_to_async
from ninja import NinjaAPI, Query
from ninja.schema import BaseModel
from ninja.decorators import decorate_view

from django.http import JsonResponse
from django_ratelimit.core import is_ratelimited
from django_ratelimit.exceptions import Ratelimited

from server.models import City
from server.openmeteo import WeatherAPI, CurrentWeather, HourlyWeather, DailyWeather

api = NinjaAPI(urls_namespace="server_api")


class CitySchema(BaseModel):
    city: str
    lat: float
    lon: float
    country: str
    population: int


@database_sync_to_async
def get_cities(q) -> List:
    queryset = City.objects.filter(city__icontains=q)[:4]
    return list(queryset.values("city", "lat", "lon", "country", "population"))


@api.get("/cities", response=List[CitySchema], url_name="city")
@decorate_view(
    cached(
        cache=RedisCache,
        serializer=PickleSerializer(),
        namespace="server_api",
    )
)
async def cities_view(request, q: Optional[str] = Query(None)) -> List:
    logger.bind(view="cities_view")

    # Check if the request is rate-limited
    if await sync_to_async(is_ratelimited)(
        request,
        fn=cities_view,
        key="ip",  # Rate limit based on IP address
        rate="10/s",  # 10 request per second
        method="GET",  # Apply to GET requests
        increment=True,  # Increment the counter
    ):
        logger.warning("Rate-limited signup attempt from IP")
        # Handle rate limit exceeded
        raise Ratelimited()

    return await get_cities(q)


async def city_search_view(request, query):
    return JsonResponse(await cities_view(request, query), safe=False)


class WeatherSchema(BaseModel):
    city: str
    country: str
    latitude: float
    longitude: float
    current: CurrentWeather
    hourly: List[HourlyWeather]
    daily: List[DailyWeather]


@api.get("/weather", response=WeatherSchema, url_name="weather")
@decorate_view(
    cached(
        cache=RedisCache,
        serializer=PickleSerializer(),
        namespace="server_api",
    )
)
async def weather_view(
    request, city: str, country: Optional[str] = Query(None)
) -> Dict[str, None]:
    logger.bind(view="weather_view")

    # Check if the request is rate-limited
    if await sync_to_async(is_ratelimited)(
        request,
        fn=weather_view,
        key="ip",  # Rate limit based on IP address
        rate="4/s",  # 1 request per second
        method="GET",  # Apply to GET requests
        increment=True,  # Increment the counter
    ):
        logger.warning("Rate-limited signup attempt from IP")
        # Handle rate limit exceeded
        raise Ratelimited()

    try:
        weather = WeatherAPI(city=city, country=country)
        data = await weather.data()
        logger.success(f"Fetched the city ({data['city']}, {data['country']})")
        return data
    except Exception as e:
        logger.exception(f"Error during index_view processing: {e}")
        raise e
