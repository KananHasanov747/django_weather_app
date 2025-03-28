from django.db import models


class City(models.Model):
    city = models.CharField(max_length=60, db_index=True)
    country = models.CharField(max_length=60)
    lat = models.FloatField()
    lon = models.FloatField()

    class Meta:
        db_table = "weather_cities"
        verbose_name_plural = "cities"
