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
        slug="springster",
        label="Springster theme",
        base_template="path/to/springster-theme-templates/base_springster-theme.html",
    )


THEMES = [
    DEFAULT_THEME,
    Theme(
        slug="zathu",
        label="Zathu theme",
        base_template="path/to/zathu-theme-templates/base_zathu-theme.html",
    ),
    Theme(
        slug="yegna",
        label="Yegna theme",
        base_template="path/to/yegna-theme-templates/base_yegna-theme.html",
    ),
    Theme(
        slug="ninyampinga",
        label="NiNyampinga theme",
        base_template="path/to/ninyampinga-theme-templates/base_ninyampinga-theme.html",
    ),
    Theme(
        slug="tujibebe",
        label="Tujibebe theme",
        base_template="path/to/tujibebe-theme-templates/base_tujibebe-theme.html",
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
