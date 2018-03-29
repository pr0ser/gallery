#!/bin/sh
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn photogallery.wsgi:application \
--workers 3 \
--bind unix:/run/gallery/gallery.socket \
--timeout 300 \
--log-level=info \
--log-file=-
