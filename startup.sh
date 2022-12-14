#!/bin/bash
if [ -n "$RUN_MIGRATIONS" ]; then
    python manage.py migrate --noinput;
fi

nginx -g 'daemon off;' &
gosu wagtail gunicorn geweb.wsgi:application --config /etc/gunicorn/config.py
