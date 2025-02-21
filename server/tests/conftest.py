import os
import pytest_asyncio
from typing import Any

from django.test import AsyncClient

from ..models import City

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


class _Auto:
    """
    Sentinel value indicating an automatic default will be used.
    """

    def __bool__(self):
        # Allow `Auto` to be used like `None` or `False` in boolean expressions
        return False


Auto: Any = _Auto()


@pytest_asyncio.fixture
async def aclient():
    return AsyncClient()


@pytest_asyncio.fixture
async def locations():
    cities = [
        City(
            city="Baku",
            country="Azerbaijan",
            lat=40.39529999999999888,
            lon=49.88219999999999744,
            population=2300500,
        ),
        City(
            city="Moscow",
            country="Russia",
            lat=55.75580000000000069,
            lon=37.61719999999999686,
            population=17332000,
        ),
        City(
            city="Tokyo",
            country="Japan",
            lat=35.68970000000000197,
            lon=139.692200000000014,
            population=37732000,
        ),
        City(
            city="Seattle",
            country="United States",
            lat=47.62109999999999844,
            lon=-122.3243999999999972,
            population=3561397,
        ),
    ]

    await City.objects.abulk_create(cities)
    yield cities

    # remove dataset from database to avoid conflicts
    for location in cities:
        await location.adelete()
