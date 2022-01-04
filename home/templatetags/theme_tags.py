from django import template

from wagtail.core.models import Page

from home.models import HomePage
from home.themes import DEFAULT_THEME, THEMES

register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_theme(context):
    """
    Returns the Theme object for the current request (derived from
    the ``page`` value in the context).
    """
    page = context.get("page")
    if isinstance(page, Page):
        if hasattr(page, "_theme"):
            return page._theme
        if hasattr(page, "theme"):
            if page.theme:
                return get_theme_from_slug(page.theme)
            return DEFAULT_THEME

        homepage = HomePage.objects.ancestor_of(page).first()
        if homepage.theme:
            theme = get_theme_from_slug(homepage.theme)
            page._theme = theme
            return theme
    return DEFAULT_THEME


def get_theme_from_slug(value):
    """
    Returns the ``Theme`` instance from ``themes.THEMES``
    with a ``slug`` value matching the provided string.
    """
    if not value:
        return
    for theme in THEMES:
        if theme.slug == value:
            return theme
    raise ValueError(f"No Theme can be found matching the slug '{value}'.")
