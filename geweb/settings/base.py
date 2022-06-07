# -*- coding: utf-8 -*-
"""
Django settings for geweb project.

Generated by 'django-admin startproject' using Django 2.2.24.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import environ
import sentry_sdk
from django.conf import global_settings, locale
from django_storage_url import dsn_configured_storage_class
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env()

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

DEFAULT_SECRET_KEY = "please-change-me"
SECRET_KEY = os.environ.get("SECRET_KEY") or DEFAULT_SECRET_KEY

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

SITE_ID = 1

INSTALLED_APPS = [
    "home",
    "articles",
    "search",
    "profiles",
    "forms",
    "comments",
    "threadedcomments",
    "django_comments",
    "django.contrib.sites",
    "social_django",
    "wagtail.contrib.settings",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.modeladmin",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.core",
    "wagtail.locales",
    "wagtailfontawesome",
    "wagtailmedia",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "wagtail.contrib.simple_translation",
]
COMMENTS_APP = "threadedcomments"
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
AUTHENTICATION_BACKENDS = [
    "social_core.backends.google.GoogleOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get(
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", ""
)

SOCIAL_AUTH_LOGIN_REDIRECT_URL = "/admin/"
SOCIAL_AUTH_WHITELISTED_EMAILS = []  # set through sitesettings
LOGIN_ERROR_URL = "/admin/"

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.social_auth.associate_by_email",
    "geweb.pipeline.auth_allowed",
    "social_core.pipeline.user.create_user",
    "geweb.pipeline.set_permissions",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

ROOT_URLCONF = "geweb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "home.context_processors.get_theme",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "wagtail.contrib.settings.context_processors.settings",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "geweb.context_processors.compress_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "geweb.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True
WAGTAIL_I18N_ENABLED = True

USE_L10N = True

USE_TZ = True

WAGTAILSIMPLETRANSLATION_SYNC_PAGE_TREE = False


STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/2.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


# Wagtail settings

WAGTAIL_SITE_NAME = "geweb"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = "http://example.com"

LANGUAGES = global_settings.LANGUAGES + [
    ("sw-tz", "Tanzanian Swahili"),
    ("ha", "Hausa"),
    ("rw", "Kinyarwanda"),
    ("id", "Indonesian"),
    ("pt", "Portuguese"),
    ("sw", "Swahili"),
    ("bn", "Bengali"),
    ("ur", "Urdu"),
    ("ny", "Chichewa"),
    ("am", "Amharic"),
]

EXTRA_LANG_INFO = {
    "rw": {
        "bidi": False,
        "code": "rw",
        "name": "Kinyarwanda",
        "name_local": "Kinyarwanda",
    },
    "ha": {"bidi": False, "code": "ha", "name": "Hausa", "name_local": "Hausa"},
    "bn": {"bidi": False, "code": "bn", "name": "Bengali", "name_local": "বাংলা"},
    "ny": {
        "bidi": False,
        "code": "ny",
        "name": "Chichewa",
        "name_local": "Chichewa",
    },
    "am": {
        "bidi": False,
        "code": "am",
        "name": "Amharic",
        "name_local": "አማርኛ",
    },
    "sw-tz": {
        "bidi": False,
        "code": "sw-tz",
        "name": "Tanzanian Swahili",
        "name_local": "Kiswahili",
    },
}
locale.LANG_INFO.update(EXTRA_LANG_INFO)
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES
TAGGIT_CASE_INSENSITIVE = True

LOGIN_URL = "/profiles/login/"

AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
AWS_DEFAULT_ACL = "public-read"

# DEFAULT_FILE_STORAGE is configured using DEFAULT_STORAGE_DSN
DEFAULT_STORAGE_DSN = os.environ.get("DEFAULT_STORAGE_DSN", "")

if DEFAULT_STORAGE_DSN:
    # dsn_configured_storage_class() requires the name of the setting
    DefaultStorageClass = dsn_configured_storage_class("DEFAULT_STORAGE_DSN")

    # Django's DEFAULT_FILE_STORAGE requires the class name
    DEFAULT_FILE_STORAGE = "geweb.settings.base.DefaultStorageClass"
    INSTALLED_APPS += [
        "storages",
    ]
elif AWS_STORAGE_BUCKET_NAME and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    INSTALLED_APPS += [
        "storages",
    ]

SENTRY_DSN = os.environ.get("SENTRY_DSN", os.environ.get("RAVEN_DSN", ""))

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=True,
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", 0.0)),
    )
