import pytest
from random import choice

from django.urls import reverse
from django.test import override_settings


@pytest.mark.django_db
@pytest.mark.asyncio
class TestServerAPI:

    @override_settings(DEBUG=True)
    async def test_openmeteo(self, aclient, locations):
        location = choice(locations)
        response = await aclient.get(
            f'{reverse("server_api:weather")}?city={location.city}&country={location.country}',
            ACCEPT="application/json",
        )

        assert response.status_code == 200
