#!/bin/sh
python manage.py migrate
python manage.py collectstatic --noinput
nice -n 19 python manage.py process_tasks &
touch /tmp/gunicorn.log
tail -n 0 -f /tmp/gunicorn.log &
gunicorn photogallery.wsgi:application \
--workers 3 \
--bind unix:/run/gallery/gallery.socket \
--timeout 300 \
--log-level=info \
--log-file=/tmp/gunicorn.log
