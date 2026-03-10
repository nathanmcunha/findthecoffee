# Copilot Instructions for Coffee Finder

## Build & Run Commands

```bash
# Start all services (DB + web app with live reload)
podman-compose up

# Rebuild after dependency changes
podman-compose build --no-cache

# Seed the database with sample data
podman-compose run --rm seed

# Run migrations only
podman-compose run --rm web python src/db/migrate.py
```

## Architecture

**Stack:** Flask + SQLAlchemy + PostgreSQL + Alembic (migrations)

**Container Runtime:** Podman (rootless) with `userns_mode: keep-id` for bind mount compatibility

### Service Topology
- `db` — PostgreSQL 16, healthcheck-gated
- `web` — Flask app, waits for DB via entrypoint gatekeeper
- `seed` — One-shot container for populating sample data

### Key Patterns
- **Repository Pattern** — `src/db/repository.py` wraps raw SQL (Spring-style DAO)
- **Singleton Database** — `src/db/connection.py` provides shared SQLAlchemy engine
- **Entrypoint Gatekeeper** — `src/docker-entrypoint.sh` blocks until DB ready, runs migrations, drops to non-root user via `gosu`

## Environment Configuration

`docker-compose.yml` = production-like defaults  
`docker-compose.override.yml` = local dev (bind mounts, Flask debug, `userns_mode: keep-id`)

Required env vars: `DATABASE_URL`, `PYTHONPATH=/app`, `FLASK_APP=src.app`

## Migrations (Alembic)

```bash
# Create new migration (with raw SQL file support)
# 1. Add src/db/alembic/versions/sql/XXXX_up.sql and XXXX_down.sql
# 2. Create corresponding .py file that loads them

# Stamp existing DB as current (skip running migrations)
podman-compose run --rm web alembic -c src/db/alembic.ini stamp head

# Run pending migrations
podman-compose run --rm web python src/db/migrate.py
```

## Conventions

- All Python imports use `src.*` prefix (e.g., `from src.db.repository import CafeRepository`)
- SQL migrations live in `src/db/alembic/versions/sql/` as `.sql` files
- Container runs as `appuser` (UID 1000) after entrypoint setup
- **Database URLs:** Code auto-converts `postgresql://` to `postgresql+psycopg://` for psycopg v3 compatibility
