# staging (or pre-production)
import sys
import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs the server for production, collects static files and compresses them."

    def add_arguments(self, parser):
        # Adding a positional argument for the server address
        parser.add_argument(
            "addrport",
            type=str,
            nargs="?",
            default="8000",
            help="Optional port number, or ipaddr:port",
        )

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

    def run_compress(self):
        """Runs compress command (using django-compressor) for production"""
        subprocess.run(
            [
                sys.executable,
                "manage.py",
                "compress",  # compresses content outside of the request/response cycle
                "--force",  # forces the generation of compressed content even if the COMPRESS_ENABLED setting is not True
            ]
        )

    def run_server(self, *args, **options):
        """Runs the Django server for production"""
        # Prepare the command to run
        addrport = options.pop("addrport")
        command = [
            "daphne",
            "config.asgi:application",  # Point to your ASGI application
            "--bind",
            "localhost",
            "--port",
            addrport.split(":")[-1],  # Extract port from addrport
        ]

        # Add any positional arguments (args) to the command list
        if args:
            command.extend(args)

        # Add any options (flags) to the command list
        if options:
            for option, value in options.items():
                if value is True:
                    # Append the flag without a value for boolean options set to True
                    command.append(f"--{option}")
                elif value not in (None, False):
                    # Append the option with its value
                    command.append(f"--{option}={value}")

        # Run the server with the constructed command
        subprocess.run(command)

    def handle(self, *args, **options):
        try:
            self.run_collectstatic()
            self.run_compress()
            self.run_server(*args, **options)
        except KeyboardInterrupt:
            sys.exit(0)
