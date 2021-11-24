from django import template
from articles.models import FooterPage

register = template.Library()


@register.inclusion_tag("home/tags/footer_page_list.html", takes_context=True)
def footer_pages(context):
    pages = []
    request = context["request"]
    site = request._wagtail_site
    if site:
        pages = FooterPage.objects.descendant_of(site.root_page)

    return {
        "request": request,
        "footers": pages,
    }
