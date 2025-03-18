import aiohttp
import asyncio

from typing import Dict
from datetime import datetime, time
from dataclasses import dataclass

from .models import City


@dataclass
class ForecastIcon:
    description: str
    day: str
    night: str


@dataclass
class CurrentWeather:
    temperature: float
    apparent_temperature: float
    icon_url: Dict
    description: str
    rain: float
    wind_speed: float


@dataclass
class HourlyWeather:
    date: str
    is_day: bool
    icon_url: Dict
    description: str
    temperature: float
    humidity: float


@dataclass
class DailyWeather:
    time: str
    day_of_week: str
    icon_url: Dict
    description: str
    temperature_max: float
    temperature_min: float
    uv_index: float


class WeatherAPI:
    static_location = "assets/icons/"
    image_formats = ["webp", "png"]
    forecast_icons = {
        0: {
            "description": "Sunny",
            "day": "clear_sky",
            "night": "clear_sky_night",
        },
        1: {
            "description": "Mainly Sunny",
            "day": "clear_sky",
            "night": "clear_sky_night",
        },
        2: {
            "description": "Partly Cloudy",
            "day": "few_clouds",
            "night": "few_clouds_night",
        },
        3: {
            "description": "Cloudy",
            "day": "scattered_clouds",
            "night": "scattered_clouds",
        },
        4: {
            "description": "Broken Cloudy",
            "day": "broken_clouds",
            "night": "broken_clouds",
        },
        45: {
            "description": "Foggy",
            "day": "mist",
            "night": "mist",
        },
        48: {
            "description": "Rime Fog",
            "day": "mist",
            "night": "mist",
        },
        51: {
            "description": "Light Drizzle",
            "day": "shower_rain",
            "night": "shower_rain",
        },
        53: {
            "description": "Drizzle",
            "day": "shower_rain",
            "night": "shower_rain",
        },
        55: {
            "description": "Heavy Drizzle",
            "day": "shower_rain",
            "night": "shower_rain",
        },
        56: {
            "description": "Light Freezing Drizzle",
            "day": "shower_rain",
            "night": "shower_rain",
        },
        57: {
            "description": "Freezing Drizzle",
            "day": "shower_rain",
            "night": "shower_rain",
        },
        61: {
            "description": "Light Rain",
            "day": "rain",
            "night": "rain",
        },
        63: {
            "description": "Rain",
            "day": "rain",
            "night": "rain",
        },
        65: {
            "description": "Heavy Rain",
            "day": "rain",
            "night": "rain",
        },
        66: {
            "description": "Light Freezing Rain",
            "day": "rain",
            "night": "rain",
        },
        67: {
            "description": "Freezing Rain",
            "day": "rain",
            "night": "rain",
        },
        71: {
            "description": "Light Snow",
            "day": "snow",
            "night": "snow",
        },
        73: {
            "description": "Snow",
            "day": "snow",
            "night": "snow",
        },
        75: {
            "description": "Heavy Snow",
            "day": "snow",
            "night": "snow",
        },
        77: {
            "description": "Snow Grains",
            "day": "snow",
            "night": "snow",
        },
        80: {
            "description": "Light Showers",
            "day": "shower_rain",
            "night": "shower_rain",
        },
        81: {
            "description": "Showers",
            "day": "shower_rain",
            "night": "shower_rain",
        },
        82: {
            "description": "Heavy Showers",
            "day": "shower_rain",
            "night": "shower_rain",
        },
        85: {
            "description": "Light Snow Showers",
            "day": "snow",
            "night": "snow",
        },
        86: {
            "description": "Snow Showers",
            "day": "snow",
            "night": "snow",
        },
        95: {
            "description": "Thunderstorm",
            "day": "thunderstorm",
            "night": "thunderstorm",
        },
        96: {
            "description": "Light Thunderstorms With Hail",
            "day": "thunderstorm",
            "night": "thunderstorm",
        },
        99: {
            "description": "Thunderstorm With Hail",
            "day": "thunderstorm",
            "night": "thunderstorm",
        },
    }

    def __init__(self, city, country) -> None:
        self.city = city
        self.country = country

    async def _init(self) -> None:
        try:
            _ = await City.objects.aget(city=self.city, country=self.country)
            self.lat = _.lat
            self.lon = _.lon
        except City.DoesNotExist:
            raise ValueError(f"City({self.city}, {self.country}) not found")

    def params(self) -> Dict:
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
        current_icon_name = WeatherAPI.forecast_icons[
            current.get("weather_code", None)
        ]["day" if bool(current.get("is_day", None)) else "night"]

        current_weather = CurrentWeather(
            temperature=round(current.get("temperature_2m", None)),
            apparent_temperature=round(current.get("apparent_temperature", None)),
            # "is_day": bool(current.get("is_day", None)),
            icon_url={
                format: self.static_location + current_icon_name + f".{format}"
                for format in self.image_formats
            },
            description=WeatherAPI.forecast_icons[current.get("weather_code", None)][
                "description"
            ],
            # precipitation=current.get("precipitation", None),
            rain=round(current.get("rain", None), 2),
            wind_speed=round(current.get("wind_speed_10m", None), 2),
            # "wind_direction": round(current.get("wind_direction_10m", None)),
        )

        hourly_weathers = []

        for w_code, dt in zip(
            hourly.get("weather_code")[:24:4],
            hourly.get("time")[:24:4],
        ):
            hourly_icon_name = WeatherAPI.forecast_icons[w_code][
                (
                    "day"
                    if time(5, 0)
                    <= datetime.strptime(dt, "%Y-%m-%dT%H:%M").time()
                    < time(20, 0)
                    else "night"
                )
            ]
            hourly_weathers.append(
                HourlyWeather(
                    date=datetime.strptime(dt, "%Y-%m-%dT%H:%M").strftime("%H:%M"),
                    is_day=(
                        True
                        if time(5, 0)
                        <= datetime.strptime(dt, "%Y-%m-%dT%H:%M").time()
                        < time(20, 0)
                        else False
                    ),
                    icon_url={
                        format: self.static_location + hourly_icon_name + f".{format}"
                        for format in self.image_formats
                    },
                    description=WeatherAPI.forecast_icons[w_code]["description"],
                    temperature=round(hourly.get("temperature_2m", None)[0]),
                    humidity=hourly.get("relative_humidity_2m", None)[0],
                )
            )

        daily_weathers = []
        for dt, w_code, max, min, uv in zip(
            daily.get("time", None),
            daily.get("weather_code", None),
            daily.get("temperature_2m_max", None),
            daily.get("temperature_2m_min", None),
            daily.get("uv_index_max", None),
        ):
            daily_icon_name = WeatherAPI.forecast_icons[w_code]["day"]
            daily_weathers.append(
                DailyWeather(
                    time=dt,
                    day_of_week=datetime.strptime(dt, "%Y-%m-%d").strftime("%A"),
                    icon_url={
                        format: self.static_location + daily_icon_name + f".{format}"
                        for format in self.image_formats
                    },
                    description=WeatherAPI.forecast_icons[w_code]["description"],
                    temperature_max=round(max),
                    temperature_min=round(min),
                    # sunrise=daily.get("sunrise", None),
                    # sunset=daily.get("sunset", None),
                    uv_index=round(uv),
                )
            )

        return {
            "city": self.city,
            "country": self.country,
            "latitude": self.lat,
            "longitude": self.lon,
            "current": current_weather,
            "hourly": hourly_weathers,
            "daily": daily_weathers,
        }
