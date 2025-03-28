from django.contrib import admin
from .models import City


class CityAdmin(admin.ModelAdmin):
    list_display = ["city", "country"]
    ordering = ["city"]


admin.site.register(City, CityAdmin)
