from django import template

from home.utils import get_theme_from_request

register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_theme(context):
    """
    Returns the Theme object for the current request (retrieved from
    the site root).
    """
    request = context["request"]
    return get_theme_from_request(request)
