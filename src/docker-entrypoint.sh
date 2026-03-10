#!/bin/sh
set -e

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-user}"
DB_NAME="${DB_NAME:-coffeedb}"

run_as_appuser() {
  if [ "$(id -u)" = "0" ]; then
    gosu appuser "$@"
  else
    "$@"
  fi
}

echo "⏳ Waiting for database at ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"; do
  sleep 1
done

echo "⚙️  Database is ready. Running migrations..."
export PYTHONPATH="${PYTHONPATH:-/app}"

if [ "$(id -u)" = "0" ]; then
  chown -R appuser:appuser /app
fi

run_as_appuser python src/db/migrate.py

echo "🚀 Starting application as non-root user (appuser)..."
if [ "$(id -u)" = "0" ]; then
  exec gosu appuser "$@"
else
  exec "$@"
fi
