#!/bin/sh
python manage.py migrate
gunicorn \
--workers 6 \
--bind 0.0.0.0:8000 \
--reload \
--access-logfile - \
--access-logformat '%(r)s %(s)s %(b)s %(L)ss' \
photogallery.wsgi:application
