#!/bin/sh
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py process_tasks &
touch /tmp/gunicorn.log
tail -n 0 -f /tmp/*.log &
gunicorn photogallery.wsgi:application \
--workers 3 \
--bind unix:/run/gallery/gallery.socket \
--log-level=info \
--log-file=/tmp/gunicorn.log
