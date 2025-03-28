#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

python3 manage.py migrate zero
python3 manage.py migrate
python3 manage.py createsuperuser --no-input
python3 -m gunicorn config.asgi:app
