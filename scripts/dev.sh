#!/bin/bash

export DJANGO_ENVIRONMENT="development"
export DJANGO_ENV_NAME=".env.dev"

# Function to run a command in the background
run_subprocess() {
    "$@" &
    pid=$!
    wait $pid
}

# Function to run Tailwind CSS watcher
run_tailwindcss() {
    ./tailwindcss-4.0.0 -i tailwind.css -o static/css/styles.css --watch
}

# Function to run the Django server
run_server() {
    uv run server.py
}

# Trap SIGINT (Ctrl+C) to terminate background processes
trap 'kill $(jobs -p)' SIGINT

# Start Tailwind CSS watcher and Django server concurrently
run_subprocess run_tailwindcss
run_subprocess run_server

# Wait for all background jobs to finish
wait
