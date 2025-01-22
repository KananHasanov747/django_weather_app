# Define an ARG for the Python version to be used
ARG PYTHON_VERSION=3.12

# Builder stage: Install all build dependencies and tools
FROM python:${PYTHON_VERSION}-alpine AS builder

# Set up environment variables
ENV PATH="/root/.rustup/bin:${PATH}"
ENV PATH="/root/.local/bin:${PATH}"
ENV PATH="/root/.cargo/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Install dependencies for building Rust packages (Alpine)
RUN apk update && apk add --no-cache \
    curl \
    build-base \
    bash \
    gcc \
    libgcc \
    libc-dev

# Install Rust and Cargo
RUN curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Set up rust toolchain
RUN rustup default stable && rustup update

# Install uv package manager
RUN pip install --no-cache-dir uv

# Clean up build dependencies
RUN apk del build-base

# Set the working directory for the builder image
WORKDIR /app

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml .

# Setting the python version
RUN uv python pin ${PYTHON_VERSION}

# Synchronize dependencies and clean caching
RUN uv sync
RUN uv clean && \
    find /app/.venv -type d -name '__pycache__' -exec rm -rf {} + && \
    find /app/.venv -name '*.so' -exec strip {} \;

# Copy the rest of the project (exlcuding the ones in .dockerignore)
COPY . .

# Final stage: Use a minimal Python image for production
FROM python:${PYTHON_VERSION}-alpine

# Adding a new user with limited privileges
RUN adduser -S appuser -D -h /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder --chown=appuser:appuser /usr/local/bin /usr/local/bin
COPY --from=builder --chown=appuser:appuser /app /app

# Copy apk libraries from the builder stage
COPY --from=builder /usr/lib/ /usr/lib/

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Run Django migrations
RUN uv run manage.py migrate 
# Import data into the database
RUN uv run -m sqlite3 db.sqlite3 < weather_cities_dump.sql > /dev/null 2>&1
