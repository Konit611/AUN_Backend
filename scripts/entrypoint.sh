#!/bin/sh
set -e

echo "[entrypoint] Waiting for database ${DB_HOST}:${DB_PORT}..."
until uv run python -c "
import os, sys, psycopg2
try:
    psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=int(os.environ.get('DB_PORT', 5432)),
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        dbname=os.environ['DB_NAME'],
    ).close()
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    sleep 1
done
echo "[entrypoint] Database is ready."

# Migrations are applied manually via Render Shell (or locally) when schema
# changes ship. Running `alembic upgrade head` on every container start OOMs
# Render's free tier (512MB).
# To migrate: open Render Shell on this service and run `uv run alembic upgrade head`.

echo "[entrypoint] Bootstrapping admin user..."
uv run python scripts/create_admin.py

echo "[entrypoint] Starting application: $*"
exec "$@"
