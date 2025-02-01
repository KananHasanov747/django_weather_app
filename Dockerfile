# Define an ARG for the Python version to be used
ARG PYTHON_VERSION=3.12

# Builder stage: Install all build dependencies and tools
FROM python:${PYTHON_VERSION}-alpine AS builder

# Set up environment variables
ENV PATH="/root/.local/bin:${PATH}"
ENV PATH="/root/.cargo/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Install dependencies for building Rust packages (Alpine)
RUN apk update && apk add --no-cache \
    curl \
    gcc \
    libc-dev
    # libffi-dev \
    # musl-dev

# Install Rust and Cargo
RUN curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Set up rust toolchain
RUN rustup default stable && rustup update

# Set config.toml to optimize the build process
RUN printf "[build]\n\
jobs = 2\n\
incremental = false\n\
[target.'cfg(all())']\n\
linker = 'rust-lld'\n\
rustflags = ['-C', 'opt-level=z', '-C', 'codegen-units=1']\n" \
    >> $HOME/.cargo/config.toml

# Install uv package manager
RUN pip install --no-cache-dir uv

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
    # --no-build-isolation \
    # Auto-scale jobs
    # --config-settings=--jobs=2 \ 
    # Safer than symlinks in containers
    --link-mode=hardlink

# Clean the __pycache__ and *.so
RUN find /app/.venv -type d -name '__pycache__' -exec rm -rf {} + && \
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
COPY --from=builder --chown=appuser /usr/local/bin /usr/local/bin
COPY --from=builder --chown=appuser /app /app

# Copy apk libraries from the builder stage
COPY --from=builder /usr/lib/ /usr/lib/

# Add unprivileged port "80" for Nginx
# RUN printf "net.ipv4.unprivileged_port_start=80" >> /etc/sysctl.conf

# Create staticfiles directory with correct ownership
# RUN mkdir -p /app/staticfiles/ && \
#     chown -R appuser /app/staticfiles && \
#     chmod -R 755 /app/staticfiles

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000
