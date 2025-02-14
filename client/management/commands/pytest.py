import subprocess

from django.core.management.base import BaseCommand


# FIX: add *args and **options for pytest command
class Command(BaseCommand):
    def handle(self, *args, **options):
        subprocess.run("pytest")
