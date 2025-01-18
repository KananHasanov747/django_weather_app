# TODO: create a build stage to optimize final image

ARG PYTHON_VERSION=3.12

# Using the Python official image from the Docker Hub
FROM python:${PYTHON_VERSION}-alpine

# Set up environment variables
ENV HOME="/root"
ENV PATH="$HOME/.rustup/bin:${PATH}"
ENV PATH="$HOME/.local/bin:${PATH}"
ENV PATH="$HOME/.cargo/bin:${PATH}"
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 

# Install dependencies for building Rust packages (Debian)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     build-essential && \
#     rm -rf /var/lib/apt/lists/* && \
#     # Remove unnecessary build tools after Rust is installed
#     apt-get purge -y build-essential && \
#     apt-get autoremove -y

# Install dependencies for building Rust packages (Alpine)
RUN apk update && apk add --no-cache \
    curl \
    build-base \
    bash \
    gcc \
    libgcc \
    libc-dev \
    # Django caching
    # memcached && \
    && \
    # Install Rust and Cargo
    curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    # Set up rust toolchain
    rustup default stable && \
    rustup update && \
    # Install uv package manager
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    # Clean up build dependencies
    apk del build-base

# Install Rust and Cargo
RUN curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Set up rust toolchain
RUN rustup default stable && \
    rustup update

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set the working directory in the container
WORKDIR /app

# Copy the rest of the project (exlcuding the ones in .dockerignore)
COPY . .

EXPOSE 8000

# Setting the python version
RUN uv python pin ${PYTHON_VERSION}

# Synchronize dependencies
RUN uv sync

# Execute commands sequentially when the container starts
# Run Django migrations
RUN uv run manage.py migrate 
# Import data into the database
RUN uv run -m sqlite3 db.sqlite3 < weather_cities_dump.sql > /dev/null 2>&1 
