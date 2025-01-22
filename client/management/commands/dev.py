import sys
import subprocess

from threading import Thread, Event

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Runs the server for development and Tailwind CSS watcher concurrently"

    def add_arguments(self, parser):
        # Adding a positional argument for the server address
        parser.add_argument(
            "addrport",
            type=str,
            nargs="?",
            default="8000",
            help="Optional port number, or ipaddr:port",
        )

    def run_subprocess(self, command, stop_event):
        """Runs a subprocess and handles its termination"""
        process = None
        try:
            process = subprocess.Popen(command)
            # Poll until the stop_event is set or process exits
            while not stop_event.is_set() and process.poll() is None:
                pass
            if process.poll() is None:
                process.terminate()  # Terminate if still running
        except KeyboardInterrupt:
            if process:
                process.terminate()
        finally:
            if process and process.poll() is None:
                process.kill()

    def run_tailwindcss(self):
        """Watches the Tailwind CSS"""
        command = [
            "tailwindcss",
            "-i",
            "tailwind.css",
            "-o",
            "static/css/styles.css",
            "--watch",
        ]

        return command

    def run_server(self, *args, **options):
        """Runs the Django server for production"""
        # Prepare the command to run
        addrport = options.pop("addrport")
        command = [sys.executable, "manage.py", "runserver", addrport]

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
        return command

    def handle(self, *args, **options):
        # Shared stop event to signal threads to terminate
        stop_event = Event()

        # Define commands for Tailwind CSS and Django server
        commands = [
            (
                self.run_tailwindcss(),
                "Tailwind CSS Watcher",
            ),
            (self.run_server(*args, **options), "Django Development Server"),
        ]

        # Create and start threads
        threads = [
            Thread(target=self.run_subprocess, args=(command, stop_event), name=name)
            for command, name in commands
        ]
        for thread in threads:
            thread.start()

        try:
            # Wait for threads to finish
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            # Signal all threads to stop
            print("\nShutting down...")
            stop_event.set()
            for thread in threads:
                thread.join()
