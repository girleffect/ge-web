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
        slug="ninyampinga",
        label="Ninyampinga theme",
        base_template="geweb/templates/ninyampinga/ninyampinga.html",
    ),
    Theme(
        slug="springster",
        label="Springster theme",
        base_template="geweb/templates/springster/springster.html",
    ),
    Theme(
        slug="yegna",
        label="Yegna theme",
        base_template="geweb/templates/yegna/yegna.html",
    ),
    Theme(
        slug="zathu",
        label="Zathu theme",
        base_template="geweb/templates/zathu/zathu.html",
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
