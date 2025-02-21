from django.db.models.functions.math import Random
from faker import Faker
import pytest

from ..models import City

fake = Faker()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_city_creation():
    for _ in range(100):
        city = fake.city()
        country = fake.country()
        lat = fake.latitude()
        lon = fake.longitude()
        population = 100_000 * Random()

        location = await City.objects.acreate(
            city=city, country=country, lat=lat, lon=lon, population=population
        )

        assert city == location.city
        assert country == location.country
        assert lat == location.lat
        assert lon == location.lon
        assert population == location.population
