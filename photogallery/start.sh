#!/bin/sh

echo "Waiting for PostgreSQL to start..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "PostgreSQL started"

python manage.py migrate
gunicorn photogallery.wsgi:application \
--workers $GUNICORN_WORKERS \
--bind 0.0.0.0:8000 \
--reload \
--timeout 120 \
--access-logfile - \
--access-logformat '%(r)s %(s)s %(b)s %(L)ss' \
