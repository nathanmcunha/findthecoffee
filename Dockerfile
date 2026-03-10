# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .
# Install to a virtual environment instead of --prefix for cleaner path handling
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# Create a non-root user (UID 1000 is standard for the first user)
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

WORKDIR /app

# Install runtime dependencies
# We include 'gosu' to safely drop from root to appuser in the entrypoint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Make venv the default Python
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY . /app

# Ensure the non-root user owns the app directory
RUN chown -R appuser:appuser /app && \
    chmod +x /app/src/docker-entrypoint.sh

# Environment variables
ENV FLASK_APP=src.app
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# We start as root to allow the entrypoint to handle any permission syncs,
# then gosu will drop us to 'appuser' for the actual app execution.
ENTRYPOINT ["/bin/sh", "/app/src/docker-entrypoint.sh"]

# Default command (will be passed to the entrypoint via "$@")
CMD ["python", "src/app.py"]
