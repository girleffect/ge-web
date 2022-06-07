from django.conf import settings
from django.contrib.auth.models import Group
from social_core.exceptions import AuthForbidden
from wagtail.core.models import Site

from home.models import SiteSettings


def set_permissions(user, is_new, *args, **kwargs):
    if user and is_new:
        group = Group.objects.get(name="Editors")
        user.groups.add(group)
        user.save()


def auth_allowed(user, backend, details, response, request, *args, **kwargs):
    _update_auth_whitelisted_emails(request)
    if (
        not backend.auth_allowed(response, details)
        or not settings.SOCIAL_AUTH_WHITELISTED_EMAILS
    ):
        raise AuthForbidden(backend)


def _update_auth_whitelisted_emails(request):
    site = Site.find_for_request(request)
    site_settings = SiteSettings.for_site(site)
    settings.SOCIAL_AUTH_WHITELISTED_EMAILS += [
        str(email)
        for email in site_settings.allowed_emails.__iter__()
        if str(email) not in settings.SOCIAL_AUTH_WHITELISTED_EMAILS
    ]
