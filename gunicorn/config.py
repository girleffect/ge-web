# See http://docs.gunicorn.org/en/latest/settings.html for a list of available
# settings. Note that the setting names are used here and not the CLI option
# names (e.g. "pidfile", not "pid").

import multiprocessing

# Set some sensible Gunicorn options, needed for things to work with Nginx
bind = "unix:/run/gunicorn/gunicorn.sock"
# umask working files (worker tmp files & unix socket) as 0o117 (i.e. chmod as
# 0o660) so that they are only read/writable by wagtail and nginx users.
umask = 0o117
# Set the worker temporary file directory to /run/gunicorn (rather than default
# of /tmp) so that all of Gunicorn's files are in one place and a tmpfs can be
# mounted at /run for better performance.
# http://docs.gunicorn.org/en/latest/faq.html#blocking-os-fchmod
worker_tmp_dir = "/run/gunicorn"

# Output the access log to stdout as well, so that it gets captured into the
# standard plaform logs and not hidden away in a volatile file inside the
# container.
# https://docs.gunicorn.org/en/stable/settings.html#accesslog
accesslog = "-"

# Set the number of workers to twice the number of cores, but limit to a
# maximum of 16.
# https://docs.gunicorn.org/en/stable/settings.html#workers
workers = min(multiprocessing.cpu_count() * 2, 1)

# Configure logging to output messages formatted similary to as defined in
# nginx/nginx.conf and geweb/settings/production.py.
logconfig_dict = {
    "disable_existing_loggers": False,
    "formatters": {
        "unified": {
            "format": "[{asctime}] {name} [{process:d}] {levelname} {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S%z",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "filters": [],
            "formatter": "unified",
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "gunicorn.access": {
            "level": "INFO",
            "propagate": True,
        },
        "gunicorn.error": {
            "level": "INFO",
            "propagate": True,
        },
    },
}
