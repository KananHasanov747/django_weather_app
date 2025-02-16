# staging (or pre-production)
import sys
import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs the server for production, collects static files and compresses them."

    def run_collectstatic(self):
        """Runs collectstatic command for production"""
        command = [
            sys.executable,
            "manage.py",
            "collectstatic",  # collects static files into STATIC_ROOT for production
            "--no-input",  # doesn't prompt for input of any kind
            "--clear",  # removes all existing files from STATIC_ROOT before copying over the new ones
        ]
        subprocess.run(command)

    def run_server(self):
        """Runs the Django server for production"""
        command = [
            sys.executable,
            # echo "127.0.0.1 weather.com" >> /etc/hosts
            # mkcert -install; cd certs/; mkcert weather.com
            "server.py",
        ]

        # Run the server with the constructed command
        subprocess.run(command)

    def handle(self, *args, **options):
        try:
            self.run_collectstatic()
            self.run_server()
        except KeyboardInterrupt:
            sys.exit(0)
