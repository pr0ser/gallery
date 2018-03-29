#!/bin/sh
sleep 5
python manage.py migrate
gunicorn photogallery.wsgi:application \
--workers 4 \
--bind 0.0.0.0:8000 \
--reload \
--timeout 120 \
--access-logfile - \
--access-logformat '%(r)s %(s)s %(b)s %(L)ss' \
