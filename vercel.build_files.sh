#!/bin/bash

export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --no-input --clear
