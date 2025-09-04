#!/usr/bin/env bash
set -e

# Wait for Postgres
if [ -n "$DB_HOST" ]; then
  echo "Waiting for DB $DB_HOST:$DB_PORT ..."
  until nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 1
  done
fi

# Django checks/migrations/static
python manage.py check --deploy || true
python manage.py migrate --noinput
# Collect static at runtime so the volume has it
python manage.py collectstatic --noinput

# Optional: lightweight health file
echo "ok" > /app/staticfiles/healthz.txt || true

# Hand off to CMD (gunicorn)
exec "$@"
