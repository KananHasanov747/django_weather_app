import pytest
import asyncio

from django.urls import reverse
from django.test import override_settings


@pytest.mark.django_db
@pytest.mark.asyncio
class TestServer:
    @override_settings(DEBUG=True)
    async def test_async_city_view(self, aclient, locations):
        """Fetching list of cities through API using 'city'"""

        async def fetch_city(city):
            """Used for making concurrent fetching"""
            # NOTE: reverse function cannot accept query params as kwargs
            response = await aclient.get(
                f'{reverse("api:city")}?q={city}', ACCEPT="application/json"
            )

            assert response.status_code == 200

        # Fetch all requests concurrently
        await asyncio.gather(*(fetch_city(location.city) for location in locations))

    @override_settings(DEBUG=True)
    async def test_async_weather_view(self, aclient, locations):
        """Fetching data through API using 'city' and 'country'"""

        async def fetch_weather(location):
            """Used for making concurrent fetching"""
            # NOTE: reverse function cannot accept query params as kwargs
            response = await aclient.get(
                f'{reverse("api:weather")}?city={location.city}&country={location.country}',
                ACCEPT="application/json",
            )
            response_json = response.json()

            assert response.status_code == 200
            assert (
                "latitude" in response_json
                and response_json["latitude"] == location.lat
            )
            assert (
                "longitude" in response_json
                and response_json["longitude"] == location.lon
            )

        # Fetch all requests concurrently
        await asyncio.gather(*(fetch_weather(location) for location in locations))
