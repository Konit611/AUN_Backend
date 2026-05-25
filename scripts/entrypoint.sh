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

echo "[entrypoint] Running database migrations..."
uv run alembic upgrade head

echo "[entrypoint] Bootstrapping admin user..."
uv run python scripts/create_admin.py

echo "[entrypoint] Starting application: $*"
exec "$@"
