import os
from os.path import abspath, dirname, join

import dj_database_url

from .base import *  # noqa

DEBUG = True

PROJECT_ROOT = os.environ.get("PROJECT_ROOT") or dirname(dirname(abspath(__file__)))
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///%s" % (join(PROJECT_ROOT, "geweb.db"),)
    )
}

SECRET_KEY = env.str("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
LOGGING = {
    "version": 1,
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
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "filters": [],
            "formatter": "unified",
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": [],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

if os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true":
    SECURE_SSL_REDIRECT = True
