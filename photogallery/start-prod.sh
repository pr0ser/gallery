#!/bin/sh
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn photogallery.wsgi:application \
--workers $GUNICORN_WORKERS \
--bind unix:/run/gallery/gallery.socket \
--timeout 300 \
--log-level=info \
--log-file=-
