import pytest
import asyncio


from django.urls import reverse
from django.test import AsyncClient, override_settings


aclient = AsyncClient(headers={"ACCEPT": "application/json"})


@pytest.mark.django_db
@pytest.mark.asyncio
class TestServerViews:
    @override_settings(DEBUG=True)
    async def test_async_city_view(self, locations):
        """Fetching list of cities through API using 'city'"""

        # Fetch all requests concurrently
        responses = await asyncio.gather(
            *(
                aclient.get(f"{reverse('server_api:city')}?q={location.city}")
                for location in locations
            )
        )

        assert responses is not None

        for response in responses:
            assert response.status_code == 200

    @override_settings(DEBUG=True)
    async def test_async_weather_view(self, locations):
        """Fetching data through API using 'city' and 'country'"""

        # Fetch all requests concurrently
        responses = await asyncio.gather(
            *(
                aclient.get(
                    f"{reverse('server_api:weather')}?city={location.city}&country={location.country}"
                )
                for location in locations
            )
        )

        assert responses is not None

        for response, location in zip(responses, locations):
            assert response.status_code == 200

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
