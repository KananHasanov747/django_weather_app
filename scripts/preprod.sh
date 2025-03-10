#!/bin/bash

export DJANGO_ENVIRONMENT="staging"
export DJANGO_ENV_NAME=".env.staging"

# Function to collect static files
run_collectstatic() {
    uv run manage.py collectstatic --no-input --clear
}

# Function to run the Django server
run_server() {
    uv run server.py
}

# Main execution
trap 'exit' SIGINT

# Collect static files and run the server
run_collectstatic
run_server
