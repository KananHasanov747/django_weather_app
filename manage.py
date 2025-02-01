#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Set ENV_NAME based on the command
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "preprod":
            os.environ.setdefault("DJANGO_ENV_NAME", ".env.staging")
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.staging")
        else:  # for development
            os.environ.setdefault("DJANGO_ENV_NAME", ".env.dev")
            os.environ.setdefault(
                "DJANGO_SETTINGS_MODULE", "config.settings.development"
            )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
