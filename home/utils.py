from home.themes import THEMES


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
