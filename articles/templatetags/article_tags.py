from django import template
from articles.models import FooterPage
from wagtail.core.models import Site

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


@register.simple_tag(takes_context=True)
def get_next_article(context, article):
    return (
        Page.objects.exact_type(ArticlePage)
        .siblings_of(article)
        .filter(path__gte=self.path)
        .live()
        .specific()
        .order_by("path")
    )
