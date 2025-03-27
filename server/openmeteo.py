import pytz
import aiohttp
import asyncio

from astral.sun import sun
from astral import LocationInfo
from typing import Dict
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ForecastIcon:
    description: str
    day: str
    night: str = ""  # Default to None, will use day if not specified

    # https://docs.python.org/3/library/dataclasses.html#dataclasses.__post_init__
    def __post_init__(self):
        if not self.night:
            self.night = self.day


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
    apparent_temperature: float
    humidity: float
    rain: float
    wind_speed: float


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
    forecast_desc = {
        0: "Sunny",
        1: "Mainly Sunny",
        2: "Partly Cloudy",
        3: "Cloudy",
        4: "Broken Cloudy",
        45: "Foggy",
        48: "Rime Fog",
        51: "Light Drizzle",
        53: "Drizzle",
        55: "Heavy Drizzle",
        56: "Light Freezing Drizzle",
        57: "Freezing Drizzle",
        61: "Light Rain",
        63: "Rain",
        65: "Heavy Rain",
        66: "Light Freezing Rain",
        67: "Freezing Rain",
        71: "Light Snow",
        73: "Snow",
        75: "Heavy Snow",
        77: "Snow Grains",
        80: "Light Showers",
        81: "Showers",
        82: "Heavy Showers",
        85: "Light Snow Showers",
        86: "Snow Showers",
        95: "Thunderstorm",
        96: "Light Thunderstorms With Hail",
        99: "Thunderstorm With Hail",
    }

    def __init__(self, city, country, lat, lon) -> None:
        self.city = city
        self.country = country
        self.lat = lat
        self.lon = lon

    def forecast_icons(self, w_code):
        desc = self.forecast_desc[w_code]
        match w_code:
            case 0 | 1:
                return ForecastIcon(desc, "clear_sky", "clear_sky_night")
            case 2:
                return ForecastIcon(desc, "few_clouds", "few_clouds_night")
            case 3:
                return ForecastIcon(desc, "scattered_clouds")
            case 4:
                return ForecastIcon(desc, "broken_clouds")
            case 45 | 48:
                return ForecastIcon(desc, "mist")
            case 51 | 53 | 55 | 56 | 57 | 80 | 81 | 82:
                return ForecastIcon(desc, "shower_rain")
            case 61 | 63 | 65 | 66 | 67:
                return ForecastIcon(desc, "rain")
            case 71 | 73 | 75 | 77 | 85 | 86:
                return ForecastIcon(desc, "snow")
            case 95 | 96 | 99:
                return ForecastIcon(desc, "thunderstorm")

    # TODO: subsitute params with local alternatives (https://grok.com/chat/ef741433-b668-4611-8e28-5632a10a60f0)
    def params(self) -> Dict:
        return {
            "latitude": self.lat,
            "longitude": self.lon,
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "uv_index_max",
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "rain",
                "precipitation_probability",
                "wind_speed_10m",
                "weather_code",
            ],
            "timezone": "auto",
            "forecast_hours": 6,
        }

    async def fetch_weather_data(self):
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

        hourly = response.get("hourly", None)
        daily = response.get("daily", None)

        timezone = response.get("timezone", None)
        location = LocationInfo("Custom", "Region", timezone, self.lat, self.lon)

        hourly_weathers = []

        for i, (w_code, dt) in enumerate(
            zip(
                hourly.get("weather_code"),
                hourly.get("time"),
            )
        ):
            tz = pytz.timezone(timezone)
            dt_obj = tz.localize(datetime.strptime(dt, "%Y-%m-%dT%H:%M"))

            s = sun(location.observer, date=dt_obj.date(), tzinfo=tz)
            sunrise = s["sunrise"]
            sunset = s["sunset"]

            is_day = True if sunrise <= dt_obj <= sunset else False

            hourly_icon_name = (
                self.forecast_icons(w_code).day
                if is_day
                else self.forecast_icons(w_code).night
            )
            hourly_weathers.append(
                HourlyWeather(
                    date=datetime.strptime(dt, "%Y-%m-%dT%H:%M").strftime("%H:%M"),
                    is_day=is_day,
                    icon_url={
                        format: self.static_location + hourly_icon_name + f".{format}"
                        for format in self.image_formats
                    },
                    description=self.forecast_desc[w_code],
                    temperature=round(hourly.get("temperature_2m", None)[i]),
                    apparent_temperature=round(
                        hourly.get("apparent_temperature", None)[i]
                    ),
                    humidity=hourly.get("relative_humidity_2m", None)[i],
                    rain=round(hourly.get("rain", None)[i], 2),
                    wind_speed=round(hourly.get("wind_speed_10m", None)[i], 2),
                )
            )

        current_weather = CurrentWeather(
            temperature=hourly_weathers[0].temperature,
            apparent_temperature=hourly_weathers[0].apparent_temperature,
            icon_url=hourly_weathers[0].icon_url,
            description=hourly_weathers[0].description,
            rain=hourly_weathers[0].rain,
            wind_speed=hourly_weathers[0].wind_speed,
        )

        daily_weathers = []
        for dt, w_code, max, min, uv in zip(
            daily.get("time", None),
            daily.get("weather_code", None),
            daily.get("temperature_2m_max", None),
            daily.get("temperature_2m_min", None),
            daily.get("uv_index_max", None),
        ):
            daily_icon_name = self.forecast_icons(w_code).day
            daily_weathers.append(
                DailyWeather(
                    time=dt,
                    day_of_week=datetime.strptime(dt, "%Y-%m-%d").strftime("%A"),
                    icon_url={
                        format: self.static_location + daily_icon_name + f".{format}"
                        for format in self.image_formats
                    },
                    description=self.forecast_desc[w_code],
                    temperature_max=round(max),
                    temperature_min=round(min),
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
