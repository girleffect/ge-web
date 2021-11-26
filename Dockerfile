# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM praekeltfoundation/python-base:3.7-stretch

# Create the user and group first as they shouldn't change often.
# Specify the UID/GIDs so that they do not change somehow and mess with the
# ownership of external volumes.
RUN addgroup --system --gid 107 wagtail \
    && adduser --system --uid 104 --ingroup wagtail wagtail \
    && mkdir /etc/gunicorn

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadbclient-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    nginx \
 && rm -rf /var/lib/apt/lists/*

# Add nginx user to wagtail group so that Nginx can read/write to gunicorn socket
RUN adduser --system nginx --ingroup wagtail
COPY nginx/ /etc/nginx/

# Install gunicorn
COPY gunicorn/ /etc/gunicorn/
RUN pip install -r /etc/gunicorn/requirements.txt

EXPOSE 8000
WORKDIR /app

COPY django-entrypoint.sh /scripts/

# Install the project requirements.
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Copy the source code of the project into the container.
COPY  . .

# Collect static files.
RUN python manage.py collectstatic --noinput --clear

ENTRYPOINT ["tini", "--", "django-entrypoint.sh"]
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
