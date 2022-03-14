from django import template
from wagtail.core.models import Page, Site

from articles.models import ArticlePage, FooterPage, SectionIndexPage, SectionPage

register = template.Library()


@register.inclusion_tag("articles/tags/footer_page_list.html", takes_context=True)
def footer_pages(context):
    request = context["request"]
    pages = []
    site = Site.find_for_request(request)
    if site:
        pages = FooterPage.objects.descendant_of(site.root_page).live()
    return {
        "request": request,
        "footers": pages,
    }


@register.simple_tag(takes_context=True)
def section_pages(context):
    request = context["request"]
    pages = []
    site = Site.find_for_request(request)
    section_index = SectionIndexPage.objects.descendant_of(site.root_page).first()
    if site and section_index:
        pages = SectionPage.objects.child_of(section_index).live()
    return pages


@register.inclusion_tag("articles/tags/breadcrumbs.html", takes_context=True)
def breadcrumbs(context):
    self = context.get("self")
    ancestors = []
    if self is not None and not self.depth <= 2:
        ancestors = (
            Page.objects.live().ancestor_of(self, inclusive=True).filter(depth__gt=3)
        )
    return {
        "ancestors": ancestors,
        "request": context["request"],
    }


@register.simple_tag(takes_context=True)
def get_next_article(context, article):
    return (
        Page.objects.filter(path__gt=article.path)
        .exact_type(ArticlePage)
        .sibling_of(article)
        .live()
        .specific()
        .order_by("path")
        .first()
    )


@register.filter
def verbose_name(instance):
    return instance._meta.verbose_name
