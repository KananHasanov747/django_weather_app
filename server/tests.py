from django.test import TestCase


class APITestCase(TestCase):
    fixtures = ["cities"]

    def setUp(self):
        self.success_locations = [
            ("Tokyo", "Japan"),
            ("Moscow", "United States"),
            ("Moscow", "Russia"),
            ("Baku", "Azerbaijan"),
            ("Paris", "France"),
        ]

    async def test_success_fetch_weather_api(self):
        """Fetching data through API using 'city' and 'country'"""
        for city, country in self.success_locations:
            response = await self.async_client.get(
                f"/api/weather?city={city}&country={country}"
            )
            self.assertEqual(response.status_code, 200)
