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
    site = Site.find_for_request(request)
    site_settings = SiteSettings.for_site(site)

    allowed_emails = [
        email.lower() for email in site_settings.allowed_emails.__iter__()
    ]
    email = details.get("email")
    allowed = False
    if email and allowed_emails:
        email = email.lower()
        allowed = email in allowed_emails
    return allowed
