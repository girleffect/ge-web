# Use an official Python runtime based on Debian 10 "buster" as a parent image.
#FROM python:3.8.1-slim-buster
FROM praekeltfoundation/django-bootstrap:py3.7-stretch

# Install the project requirements.
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Copy the source code of the project into the container.
COPY  . .

# Collect static files.
RUN python manage.py collectstatic --noinput --clear

# Runtime command that executes when "docker run" is called, it does the
# following:
#   1. Migrate the database.
#   2. Start the application server.
# WARNING:
#   Migrating database at the same time as starting the server IS NOT THE BEST
#   PRACTICE. The database should be migrated manually or using the release
#   phase facilities of your hosting platform. This is used only so the
#   Wagtail instance can be started with a simple "docker run" command.
CMD set -xe; python manage.py migrate --noinput; gunicorn geweb.wsgi:application
