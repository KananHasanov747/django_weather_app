import aiohttp
import requests
from loguru import logger

from ipware import get_client_ip
from django.core.cache import cache

from server.models import City


def get_location(request):
    # Get the client's IP address
    client_ip, is_routable = get_client_ip(request)
    if not is_routable or not client_ip:
        return {}

    # Check if location in cache; otherwise, create a new one
    cache_key = f"location_{client_ip}"
    if location := cache.get(cache_key):
        return location

    # Fetch location data from ipinfo
    try:
        response = requests.get(f"https://ipinfo.io/{client_ip}/json")
        data = response.json()  # city, country, loc

        # Check if data is not empty
        if loc := data.get("loc", None):
            lat, lon = loc.split(",")
            # Use Haversine formula to find the closest distance to the registered city (<29 miles)
            # 3959 for miles, 6371 for km
            # NOTE: Postgres cannot work without subquery; otherwise, it'll scream "distance does not exist"
            query = f"""
                    SELECT * 
                    FROM (
                      SELECT id, lat, lon,
                        (3959 * acos(
                            cos(radians({lat})) * cos(radians(lat)) *
                            cos(radians(lon) - radians({lon})) +
                            sin(radians({lat})) * sin(radians(lat))
                        )) AS distance
                      FROM weather_cities
                    ) AS subquery
                    WHERE distance < 29
                    ORDER BY distance
                    LIMIT 1;
                """

            obj = City.objects.raw(query)[0]

            cache.set(
                cache_key,
                location := {
                    "city": obj.city,
                    "country": obj.country,
                    "lat": obj.lat,
                    "lon": obj.lon,
                },
                timeout=86400,
            )  # 1 day
            return location
        else:
            return {}

    except aiohttp.ClientResponseError as e:
        logger.exception(f"HTTP error: {e.status}")
        raise e
    except Exception as e:
        logger.exception(e)
        raise e
