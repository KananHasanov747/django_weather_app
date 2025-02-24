# Define an ARG for the Python version to be used
ARG PYTHON_VERSION=3.12

# Builder stage: Install all build dependencies and tools
FROM python:${PYTHON_VERSION}-alpine AS builder

# Set up environment variables
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies for building Rust packages (Alpine)

RUN apk update
RUN apk add --no-cache curl

# TODO: move .venv file into /opt/venv and run from there (e.g., /opt/venv/bin/python or /opt/venv/bin/pip)

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set the working directory for the builder image
WORKDIR /app

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml .

# Setting the python version
RUN uv python pin ${PYTHON_VERSION}

# Synchronize dependencies and clean caching
RUN uv sync \
 --no-cache \
 --no-dev \
 --link-mode=hardlink

# Clean the **pycache** and \*.so
RUN find /app/.venv -type d -name '**pycache**' -exec rm -rf {} + && \
    find /app/.venv -name '\*.so' -exec strip {} \;

# Copy the rest of the project (exlcuding the ones in .dockerignore)
COPY . .

# Final stage: Use a minimal Python image for production
FROM python:${PYTHON_VERSION}-alpine

# FIX: appuser cannot interact with postgres
# Adding a new user with limited privileges
# RUN adduser -S appuser -D -h /app

# Set environment variables
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files from the builder stage
# COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.local/bin /root/.local/bin
COPY --from=builder /app /app

# TODO: create entrypoint.sh
# TODO: add superuser via /opt/venv/bin/python manage.py createsuperuser --username USERNAME --noinput
