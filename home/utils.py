from wagtail.core.models import Site
from home.themes import DEFAULT_THEME, THEMES


def get_theme_from_request(request):
    """
    Returns the Theme object for the current request.
    """
    site = Site.find_for_request(request)
    theme = DEFAULT_THEME
    if site:
        if site.root_page.specific.theme:
            theme = get_theme_from_slug(site.root_page.specific.theme)
    return theme

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
