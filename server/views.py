from typing import List, Optional
from django.http import JsonResponse
from ninja import NinjaAPI, Query
from ninja.schema import BaseModel
from channels.db import database_sync_to_async

# from datetime import time

from server.models import City
from server.openmeteo import WeatherAPI, CurrentWeather, HourlyWeather, DailyWeather

api = NinjaAPI(urls_namespace="api")


class CitySchema(BaseModel):
    city: str
    lat: float
    lon: float
    country: str
    population: int


@database_sync_to_async
def get_cities(q):
    queryset = City.objects.filter(city__icontains=q)[:4]
    return list(queryset.values("city", "lat", "lon", "country", "population"))


@api.get("/cities", response=List[CitySchema], url_name="city")
async def cities_view(request, q: Optional[str] = Query(None)):
    return await get_cities(q)


async def city_search_view(request, query):
    return JsonResponse(await cities_view(request, query), safe=False)


# class CurrentWeather(BaseModel):
#     temperature: float
#     apparent_temperature: float
#     # is_day: int
#     icon_url: str
#     # precipitation: float
#     rain: float
#     # weather_code: int
#     wind_speed: float
#     # wind_direction: float
#
#
# class HourlyWeather(BaseModel):
#     date: List[time]
#     icon_url: List[str]
#     description: List[str]
#     # is_day: List[bool]
#     temperature: List[float]
#     humidity: List[int]
#     # weather_code: List[int]
#
#
# class DailyWeather(BaseModel):
#     time: List[str]
#     days_of_week: List[str]
#     icon_url: List[str]
#     description: List[str]
#     # weather_code: List[int]
#     temperature_max: List[float]
#     temperature_min: List[float]
#     # sunrise: List[str]
#     # sunset: List[str]
#     uv_index: List[int]


class WeatherSchema(BaseModel):
    city: str
    country: str
    latitude: float
    longitude: float
    current: CurrentWeather
    hourly: List[HourlyWeather]
    daily: List[DailyWeather]


@api.get("/weather", response=WeatherSchema, url_name="weather")
async def weather_view(request, city: str, country: Optional[str] = Query(None)):
    try:
        weather = WeatherAPI(city=city, country=country)
        data = await weather.data()
        return data
    except Exception as e:
        raise e
