from django import template
from articles.models import FooterPage
from wagtail.core.models import Site

register = template.Library()


@register.inclusion_tag("home/tags/footer_page_list.html", takes_context=True)
def footer_pages(context):
    request = context["request"]
    site = Site.find_for_request(request)
    pages = FooterPage.objects.descendant_of(site.root_page)
    return {
        "request": request,
        "footers": pages,
    }
