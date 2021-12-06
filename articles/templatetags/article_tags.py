from django import template
from articles.models import FooterPage
from wagtail.core.models import Page, Site

register = template.Library()


@register.inclusion_tag("articles/tags/footer_page_list.html", takes_context=True)
def footer_pages(context):
    request = context["request"]
    pages = []
    site = Site.find_for_request(request)
    if site:
        pages = FooterPage.objects.descendant_of(site.root_page)
    return {
        "request": request,
        "footers": pages,
    }


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
