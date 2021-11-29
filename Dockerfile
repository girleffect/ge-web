FROM praekeltfoundation/django-bootstrap:py3.7-stretch

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Copy the source code of the project into the container.
COPY . .

# Install the project requirements.
RUN pip install .

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Collect static files.
RUN python manage.py collectstatic --noinput --clear

# Runtime command that executes when "docker run" is called
CMD ["geweb.wsgi:application"]
