import aiohttp
import asyncio
from .models import City

from datetime import datetime, time


class WeatherAPI:
    forecast_icons = {
        0: {
            "description": "Sunny",
            "day": "assets/icons/clear_sky.png",
            "night": "assets/icons/clear_sky_night.png",
        },
        1: {
            "description": "Mainly Sunny",
            "day": "assets/icons/clear_sky.png",
            "night": "assets/icons/clear_sky_night.png",
        },
        2: {
            "description": "Partly Cloudy",
            "day": "assets/icons/few_clouds.png",
            "night": "assets/icons/few_clouds_night.png",
        },
        3: {
            "description": "Cloudy",
            "day": "assets/icons/scattered_clouds.png",
            "night": "assets/icons/scattered_clouds.png",
        },
        4: {
            "description": "Broken Cloudy",
            "day": "assets/icons/broken_clouds.png",
            "night": "assets/icons/broken_clouds.png",
        },
        45: {
            "description": "Foggy",
            "day": "assets/icons/mist.png",
            "night": "assets/icons/mist.png",
        },
        48: {
            "description": "Rime Fog",
            "day": "assets/icons/mist.png",
            "night": "assets/icons/mist.png",
        },
        51: {
            "description": "Light Drizzle",
            "day": "assets/icons/shower_rain.png",
            "night": "assets/icons/shower_rain.png",
        },
        53: {
            "description": "Drizzle",
            "day": "assets/icons/shower_rain.png",
            "night": "assets/icons/shower_rain.png",
        },
        55: {
            "description": "Heavy Drizzle",
            "day": "assets/icons/shower_rain.png",
            "night": "assets/icons/shower_rain.png",
        },
        56: {
            "description": "Light Freezing Drizzle",
            "day": "assets/icons/shower_rain.png",
            "night": "assets/icons/shower_rain.png",
        },
        57: {
            "description": "Freezing Drizzle",
            "day": "assets/icons/shower_rain.png",
            "night": "assets/icons/shower_rain.png",
        },
        61: {
            "description": "Light Rain",
            "day": "assets/icons/rain.png",
            "night": "assets/icons/rain.png",
        },
        63: {
            "description": "Rain",
            "day": "assets/icons/rain.png",
            "night": "assets/icons/rain.png",
        },
        65: {
            "description": "Heavy Rain",
            "day": "assets/icons/rain.png",
            "night": "assets/icons/rain.png",
        },
        66: {
            "description": "Light Freezing Rain",
            "day": "assets/icons/rain.png",
            "night": "assets/icons/rain.png",
        },
        67: {
            "description": "Freezing Rain",
            "day": "assets/icons/rain.png",
            "night": "assets/icons/rain.png",
        },
        71: {
            "description": "Light Snow",
            "day": "assets/icons/snow.png",
            "night": "assets/icons/snow.png",
        },
        73: {
            "description": "Snow",
            "day": "assets/icons/snow.png",
            "night": "assets/icons/snow.png",
        },
        75: {
            "description": "Heavy Snow",
            "day": "assets/icons/snow.png",
            "night": "assets/icons/snow.png",
        },
        77: {
            "description": "Snow Grains",
            "day": "assets/icons/snow.png",
            "night": "assets/icons/snow.png",
        },
        80: {
            "description": "Light Showers",
            "day": "assets/icons/shower_rain.png",
            "night": "assets/icons/shower_rain.png",
        },
        81: {
            "description": "Showers",
            "day": "assets/icons/shower_rain.png",
            "night": "assets/icons/shower_rain.png",
        },
        82: {
            "description": "Heavy Showers",
            "day": "assets/icons/shower_rain.png",
            "night": "assets/icons/shower_rain.png",
        },
        85: {
            "description": "Light Snow Showers",
            "day": "assets/icons/snow.png",
            "night": "assets/icons/snow.png",
        },
        86: {
            "description": "Snow Showers",
            "day": "assets/icons/snow.png",
            "night": "assets/icons/snow.png",
        },
        95: {
            "description": "Thunderstorm",
            "day": "assets/icons/thunderstorm.png",
            "night": "assets/icons/thunderstorm.png",
        },
        96: {
            "description": "Light Thunderstorms With Hail",
            "day": "assets/icons/thunderstorm.png",
            "night": "assets/icons/thunderstorm.png",
        },
        99: {
            "description": "Thunderstorm With Hail",
            "day": "assets/icons/thunderstorm.png",
            "night": "assets/icons/thunderstorm.png",
        },
    }

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
                # "precipitation",
                "rain",
                "weather_code",
                "wind_speed_10m",
                # "wind_direction_10m",
            ],
            "hourly": ["temperature_2m", "relative_humidity_2m", "weather_code"],
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                # "sunrise",
                # "sunset",
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

        hourly_date = []
        hourly_is_day = []
        hourly_icon_url = []
        hourly_desc = []
        for w_code, dt in zip(
            hourly.get("weather_code")[:24:4],
            hourly.get("time")[:24:4],
        ):
            hourly_date.append(
                datetime.strptime(dt, "%Y-%m-%dT%H:%M").strftime("%H:%M")
            )
            hourly_is_day.append(
                True
                if time(5, 0)
                <= datetime.strptime(dt, "%Y-%m-%dT%H:%M").time()
                < time(20, 0)
                else False
            )
            hourly_icon_url.append(
                WeatherAPI.forecast_icons[w_code][
                    (
                        "day"
                        if time(5, 0)
                        <= datetime.strptime(dt, "%Y-%m-%dT%H:%M").time()
                        < time(20, 0)
                        else "night"
                    )
                ],
            )
            hourly_desc.append(
                WeatherAPI.forecast_icons[w_code]["description"],
            )

        daily_icon_url = []
        daily_desc = []
        daily_temp_max = []
        daily_temp_min = []
        daily_uv_index = []
        for w_code, max, min, uv in zip(
            daily.get("weather_code", None),
            daily.get("temperature_2m_max", None),
            daily.get("temperature_2m_min", None),
            daily.get("uv_index_max", None),
        ):
            daily_icon_url.append(WeatherAPI.forecast_icons[w_code]["day"])
            daily_desc.append(WeatherAPI.forecast_icons[w_code]["description"])
            daily_temp_max.append(round(max))
            daily_temp_min.append(round(min))
            daily_uv_index.append(round(uv))

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
                # "is_day": bool(current.get("is_day", None)),
                "icon_url": WeatherAPI.forecast_icons[
                    current.get("weather_code", None)
                ]["day" if bool(current.get("is_day", None)) else "night"],
                "description": WeatherAPI.forecast_icons[
                    current.get("weather_code", None)
                ],
                "precipitation": current.get("precipitation", None),
                "rain": round(current.get("rain", None), 2),
                # "weather_code": current.get("weather_code", None),
                "wind_speed": round(current.get("wind_speed_10m", None), 2),
                # "wind_direction": round(current.get("wind_direction_10m", None)),
            },
            "hourly": {
                "date": hourly_date,
                "is_day": hourly_is_day,
                "icon_url": hourly_icon_url,
                "description": hourly_desc,
                "temperature": [
                    round(_) for _ in hourly.get("temperature_2m", None)[:24:4]
                ],
                "humidity": hourly.get("relative_humidity_2m", None)[:24:4],
                # "weather_code": hourly.get("weather_code")[:24:4],
            },
            "daily": {
                "time": daily.get("time"),
                "days_of_week": days_of_week,
                "icon_url": daily_icon_url,
                "description": daily_desc,
                # "weather_code": daily.get("weather_code", None),
                "temperature_max": daily_temp_max,
                "temperature_min": daily_temp_min,
                # "sunrise": daily.get("sunrise", None),
                # "sunset": daily.get("sunset", None),
                "uv_index": daily_uv_index,
            },
        }
