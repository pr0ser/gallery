#!/bin/sh
python manage.py migrate
pytgon manage.py collectstatic --noinput
python manage.py process_tasks &
touch /var/log/gunicorn.log
touch /var/log/access.log
tail -n 0 -f /var/log/*.log &
gunicorn photogallery.wsgi:application \
--workers 4 \
--bind unix:/run/gunicorn.socket \
--log-level=info \
--log-file=/var/log/gunicorn.log \
--access-logfile=/var/log/access.log \
