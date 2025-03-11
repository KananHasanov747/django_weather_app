import os
from django.db import migrations
from django.conf import settings

import environ

env = environ.Env(DJANGO_POSTGRES=(bool, False))


def load_sql():
    file_path = os.path.join(settings.BASE_DIR, "weather_cities_dump.sql")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def load_cities_sqlite(apps, schema_editor):
    sql_content = load_sql()
    cursor = schema_editor.connection.cursor()

    # set PRAGMA settings to speed up the loading
    cursor.execute("PRAGMA synchronous=3;")
    cursor.execute("PRAGMA cache_size=10000;")
    cursor.execute("PRAGMA journal_mode=MEMORY;")

    cursor.executescript(sql_content)


def unload_cities_sqlite(apps, schema_editor):
    # reverse operation: delete all rows from the City table
    City = apps.get_model("server", "City")
    City.objects.all().delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [("server", "0001_initial")]

    if env("DJANGO_POSTGRES"):
        sql_statements = load_sql()
        operations = [
            migrations.RunSQL(
                sql_statements, reverse_sql="DELETE FROM weather_cities;"
            ),
        ]

    else:
        operations = [
            migrations.RunPython(load_cities_sqlite, reverse_code=unload_cities_sqlite),
        ]
