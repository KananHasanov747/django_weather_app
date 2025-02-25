import os
from django.db import migrations
from django.conf import settings


def load_cities(apps, schema_editor):
    file_path = os.path.join(settings.BASE_DIR, "weather_cities_dump.sql")

    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    cursor = schema_editor.connection.cursor()

    if schema_editor.connection.vendor == "sqlite":
        # set PRAGMA settings to speed up the loading
        cursor.execute("PRAGMA synchronous=OFF;")
        cursor.execute("PRAGMA cache_size=10000;")
        cursor.execute("PRAGMA journal_mode=MEMORY;")

        cursor.executescript(sql_content)

    else:  # postgres & others
        statements = sql_content.split(";")
        for statement in statements:
            statement = statement.strip()
            if statement:
                cursor.execute(statement)


def unload_cities(apps, schema_editor):
    # reverse operation: delete all rows from the City table
    City = apps.get_model("server", "City")
    City.objects.all().delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("server", "0001_initial")]

    operations = [
        migrations.RunPython(load_cities, reverse_code=unload_cities),
    ]
