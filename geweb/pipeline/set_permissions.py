from django.conf import settings
from social_core.exceptions import AuthForbidden
from wagtail.core.models import Site

from home.models import SiteSettings


def set_permissions(user, is_new, *args, **kwargs):
    if user and is_new:
        user.is_superuser = True
        user.save()


def auth_allowed(user, backend, details, response, *args, **kwargs):
    _update_auth_whitelisted_emails()
    if not backend.auth_allowed(response, details):
        user.delete()
        raise AuthForbidden(backend)


def _update_auth_whitelisted_emails():
    site = Site.objects.first()
    site_settings = SiteSettings.for_site(site)
    settings.SOCIAL_AUTH_WHITELISTED_EMAILS += [
        str(email)
        for email in site_settings.allowed_emails.__iter__()
        if str(email) not in settings.SOCIAL_AUTH_WHITELISTED_EMAILS
    ]
