from django.contrib import admin
from .models import City


class CityAdmin(admin.ModelAdmin):
    list_display = ["city", "country", "population"]
    ordering = ["city"]


admin.site.register(City, CityAdmin)
