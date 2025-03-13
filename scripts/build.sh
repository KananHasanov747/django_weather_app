#!/bin/bash
# only use for hosting platforms or other local machines;
# Docker/Podman already does the same automatically

set -a # Automatically export all variables
source .env.prod
set +a # Disable automatic exporting
# in terminal, do `set -a; source .env.prod; set +a`

# Detect OS type and install dependencies accordingly
case "$OSTYPE" in
  "linux-gnu"*)
    # Ubuntu, Debian, or Fedora
    apt-get update
    apt-get install curl -y
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.local/bin/env" # env.fish for fish
    ;;
  "darwin"*)
    # macOS
    # Install Homebrew package manager
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Install uv package manager
    brew install uv
    # Alternative: curl -LsSf https://astral.sh/uv/install.sh | sh
    ;;
  "cygwin" | "msys" | "win32" | "freebsd"*)
    # Placeholder for unsupported or less common systems
    echo "Unsupported OS type: $OSTYPE"
    exit 1
    ;;
  *)
    # Unknown OS
    echo "Unknown OS type: $OSTYPE"
    exit 1
    ;;
esac


uv run --no-dev --no-cache manage.py collectstatic --no-input --clear
uv run --no-dev --no-cache manage.py migrate
uv run --no-dev --no-cache -m gunicorn config.asgi:application --bind :8000 --workers 3 --worker-class uvicorn.workers.UvicornWorker
