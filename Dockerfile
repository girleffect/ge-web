# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM praekeltfoundation/python-base:3.7-stretch

# Create the user and group first as they shouldn't change often.
# Specify the UID/GIDs so that they do not change somehow and mess with the
# ownership of external volumes.
RUN addgroup --system --gid 107 wagtail \
    && adduser --system --uid 104 --ingroup wagtail wagtail \
    && mkdir /etc/gunicorn

# Install libpq for psycopg2 for PostgreSQL support
 RUN apt-get-install.sh libpq5

# Install a modern Nginx and configure
ENV NGINX_VERSION=1.14.2 \
    NGINX_GPG_KEY=573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62
RUN set -ex; \
    fetchDeps=" \
        wget \
        $(command -v gpg > /dev/null || echo 'dirmngr gnupg') \
    "; \
    apt-get-install.sh $fetchDeps; \
    wget https://nginx.org/keys/nginx_signing.key; \
    [ "$(gpg --batch -q --with-fingerprint --with-colons nginx_signing.key | awk -F: '/^fpr:/ { print $10 }')" \
        = $NGINX_GPG_KEY ]; \
    apt-key add nginx_signing.key; \
    codename="$(. /etc/os-release; echo $VERSION | grep -oE [a-z]+)"; \
    echo "deb http://nginx.org/packages/debian/ $codename nginx" > /etc/apt/sources.list.d/nginx.list; \
    rm nginx_signing.key; \
    apt-get purge -y --auto-remove $fetchDeps; \
    \
    apt-get-install.sh "nginx=$NGINX_VERSION-1\~$codename"; \
    rm /etc/nginx/conf.d/default.conf; \
# Add nginx user to wagtail group so that Nginx can read/write to gunicorn socket
    adduser nginx wagtail
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
