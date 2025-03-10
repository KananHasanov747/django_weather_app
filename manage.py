#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import environ


def main():
    """Run administrative tasks."""
    # Set ENV_NAME based on the command
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in ("pytest", "check"):
            os.environ["DJANGO_ENVIRONMENT"] = "production"
            os.environ["DJANGO_ENV_NAME"] = ".env.prod"

        elif command == "preprod":
            os.environ["DJANGO_ENVIRONMENT"] = "staging"
            os.environ["DJANGO_ENV_NAME"] = ".env.staging"
        else:  # for development
            os.environ["DJANGO_ENVIRONMENT"] = "development"
            os.environ["DJANGO_ENV_NAME"] = ".env.dev"
    else:
        os.environ["DJANGO_ENVIRONMENT"] = "development"
        os.environ["DJANGO_ENV_NAME"] = ".env.dev"

    env = environ.Env()
    environ.Env.read_env(env("DJANGO_ENV_NAME"))
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

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
