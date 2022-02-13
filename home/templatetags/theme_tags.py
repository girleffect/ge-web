from django import template
from wagtail.core.models import Site

from home.themes import DEFAULT_THEME
from home.utils import get_theme_from_slug

register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_theme(context):
    """
    Returns the Theme object for the current request (retrieved from
    the site root).
    """
    request = context["request"]
    site = Site.find_for_request(request)
    theme = DEFAULT_THEME
    if site:
        if site.root_page.specific.theme:
            theme = get_theme_from_slug(site.root_page.specific.theme)
    return theme
