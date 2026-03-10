#!/bin/bash
set -e

# Extract host from DATABASE_URL
# Format: postgresql://user:password@HOST:PORT/db
# We handle cases where :PORT might be missing
DB_HOST=$(echo $DATABASE_URL | sed -e 's|.*@\(.*\):.*|\1|' | cut -d/ -f1 | cut -d: -f1)

# Default to 'db' if extraction fails
DB_HOST=${DB_HOST:-db}

echo "⏳ Waiting for database at $DB_HOST..."
until pg_isready -h "$DB_HOST" -U user -d coffeedb; do
  sleep 1
done

echo "⚙️  Database is ready. Running migrations..."
export PYTHONPATH=$PYTHONPATH:/app
# In Podman, we run migrations as the current user (root inside container) 
# and then drop to appuser for the app itself.
alembic -c db/alembic.ini upgrade head

echo "🚀 Starting application as non-root user (appuser)..."
# 'gosu' drops privileges from root to 'appuser' for the final command
exec gosu appuser "$@"
