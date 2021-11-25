# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.8.1-slim-buster

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadbclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

# Install and configure gunicorn
RUN pip install "gunicorn==20.0.4"
RUN mkdir /etc/gunicorn
COPY gunicorn/ /etc/gunicorn/

# Add user and group that will be used in the container.
RUN addgroup --system wagtail && adduser --system wagtail --ingroup wagtail

# Make sure gunicorn files are owned by the user
RUN chown -R wagtail:wagtail /etc/gunicorn/

# Install and configure Nginx
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends nginx
COPY nginx/sites-available/wagtail.conf /etc/nginx/sites-available/wagtail.conf
COPY nginx/sites-available/wagtail.conf /etc/nginx/sites-enabled/wagtail.conf
# Add the user Nginx is using to the wagtail group so it can write to the socket
RUN sed -i 's/user www-data;/user wagtail;/' /etc/nginx/nginx.conf
RUN chown -R wagtail:wagtail /var/log/nginx;
RUN chmod -R 755 /var/log/nginx;

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Install the project requirements.
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown wagtail:wagtail /app

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .

# Use user "wagtail" to run the build commands below and the server itself.
USER wagtail

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
CMD set -xe; \
    nginx -g 'daemon off;'; \
    service nginx reload; \
    python manage.py migrate --noinput; \
    gunicorn geweb.wsgi:application --config /etc/gunicorn/conf.py
