from django import template
from articles.models import FooterPage, ArticlePage
from wagtail.core.models import Site, Page

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
        Page.objects.filter(path__gt=article.path)
        .exact_type(ArticlePage)
        .sibling_of(article)
        .live()
        .specific()
        .order_by("path")
        .first()
    )
