import pytest
from aiocache import Cache

from django.urls import reverse
from django.test import override_settings


@pytest.mark.django_db
@pytest.mark.asyncio
class TestOpenMeteo:
    @override_settings(DEBUG=True)
    async def test_aiocache(self, aclient):
        response = await aclient.get(
            f'{reverse("api:weather")}?city=Moscow&country=Russia'
        )
        cache = Cache(Cache.MEMCACHED)

        assert cache.exists("key") is True
