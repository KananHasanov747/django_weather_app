# Set the python version
ARG PYTHON_VERSION=3.12

# Pull the image
FROM python:${PYTHON_VERSION}-alpine

# Set up environment variables
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apk update
RUN apk add --no-cache curl

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set the working directory
WORKDIR /app

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml .

# Setting the python version
RUN uv python pin ${PYTHON_VERSION}

# Synchronize dependencies and clean caching
RUN uv sync --no-cache --no-dev

# Copy the rest of the project (exlcuding the ones in .dockerignore)
COPY . .
