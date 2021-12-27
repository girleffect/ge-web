from dataclasses import dataclass
from operator import itemgetter


@dataclass
class Theme:
    """Class for defining a site-wide 'themes'. For notes on dataclasses, see:
    Ref: https://docs.python.org/3/whatsnew/3.7.html#whatsnew37-pep557"""

    frozen = True
    slug: str
    label: str
    base_template: str


DEFAULT_THEME = Theme(
    slug="default",
    label="Default",
    base_template="path/to/templates/base_default.html",
)


THEMES = [
    DEFAULT_THEME,
    Theme(
        slug="a-custom-theme",
        label="An example theme",
        base_template="path/to/a-custom-theme-templates/base_a-custom-theme.html",
    ),
    Theme(
        slug="springster-theme",
        label="Springster theme",
        base_template="path/to/springster-theme-templates/base_springster-theme.html",
    ),
    Theme(
        slug="zathu-theme",
        label="Zathu theme",
        base_template="path/to/zathu-theme-templates/base_zathu-theme.html",
    ),
]


def get_theme_choices():
    # Generate alphabetically ordered choices
    choices = []
    for theme in THEMES:
        choices.append((theme.slug, theme.label))
    choices.sort(key=itemgetter(1))
    return choices


THEME_CHOICES = tuple(get_theme_choices())
