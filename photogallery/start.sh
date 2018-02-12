#!/bin/sh
python manage.py migrate
nice -n 19 python manage.py process_tasks &
nice -n 19 python manage.py process_tasks &
nice -n 19 python manage.py process_tasks &
nice -n 19 python manage.py process_tasks &
gunicorn photogallery.wsgi:application \
--workers 4 \
--bind 0.0.0.0:8000 \
--reload \
--timeout 120 \
--access-logfile - \
--access-logformat '%(r)s %(s)s %(b)s %(L)ss' \
