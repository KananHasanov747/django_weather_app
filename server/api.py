import aiohttp
import asyncio
from .models import City

from datetime import datetime, time


class WeatherAPI:
    def __init__(self, city, country):
        self.city = city
        self.country = country

    async def _init(self):
        try:
            _ = await City.objects.aget(city=self.city, country=self.country)
            self.lat = _.lat
            self.lon = _.lon
        except City.DoesNotExist:
            raise ValueError(f"City({self.city}, {self.country}) not found")

    def params(self):
        return {
            "latitude": self.lat,
            "longitude": self.lon,
            "current": [
                "temperature_2m",
                "apparent_temperature",
                "is_day",
                "precipitation",
                "rain",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
            ],
            "hourly": ["temperature_2m", "relative_humidity_2m", "weather_code"],
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "sunrise",
                "sunset",
                "uv_index_max",
            ],
            # "timezone": "auto",
        }

    async def fetch_weather_data(self):
        await self._init()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.open-meteo.com/v1/forecast", params=self.params()
                ) as response:
                    return await response.json()
        except aiohttp.ClientResponseError as e:
            raise ValueError(f"Error fetching weather data: {e}")
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Timeout error: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {e}")

    async def data(self):
        response = await self.fetch_weather_data()
        current = response.get("current", None)
        hourly = response.get("hourly", None)
        daily = response.get("daily", None)

        days_of_week = [
            datetime.strptime(dt, "%Y-%m-%d").strftime("%A") for dt in daily.get("time")
        ]

        return {
            "city": self.city,
            "country": self.country,
            "latitude": self.lat,
            "longitude": self.lon,
            "current": {
                "temperature": round(current.get("temperature_2m", None)),
                "apparent_temperature": round(
                    current.get("apparent_temperature", None)
                ),
                "is_day": int(current.get("is_day", None)),
                "precipitation": current.get("precipitation", None),
                "rain": round(current.get("rain", None), 2),
                "weather_code": current.get("weather_code", None),
                "wind_speed": round(current.get("wind_speed_10m", None), 2),
                "wind_direction": round(current.get("wind_direction_10m", None)),
            },
            "hourly": {
                "date": [
                    datetime.strptime(dt, "%Y-%m-%dT%H:%M").strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                    for dt in hourly.get("time")[:24:4]
                ],
                "is_day": [
                    (
                        True
                        if time(5, 0)
                        <= datetime.strptime(dt, "%Y-%m-%dT%H:%M").time()
                        < time(20, 0)
                        else False
                    )
                    for dt in hourly.get("time")[:24:4]
                ],
                "temperature": [
                    round(_) for _ in hourly.get("temperature_2m", None)[:24:4]
                ],
                "humidity": hourly.get("relative_humidity_2m", None)[:24:4],
                "weather_code": hourly.get("weather_code")[:24:4],
            },
            "daily": {
                "time": daily.get("time"),
                "days_of_week": days_of_week,
                "weather_code": daily.get("weather_code", None),
                "temperature_max": [
                    round(_) for _ in daily.get("temperature_2m_max", None)
                ],
                "temperature_min": [
                    round(_) for _ in daily.get("temperature_2m_min", None)
                ],
                "sunrise": daily.get("sunrise", None),
                "sunset": daily.get("sunset", None),
                "uv_index": [round(_) for _ in daily.get("uv_index_max", None)],
            },
        }
