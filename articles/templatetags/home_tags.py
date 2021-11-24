from django import template
from articles.models import FooterPage
from wagtail.core.models import Site
from home.models import SiteSettings

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


@register.inclusion_tag("home/tags/social_media_footer.html", takes_context=True)
def social_media_footer(context, page=None):
    site = Site.find_for_request(context["request"])
    social_media = SiteSettings.for_site(site).social_media_links_on_footer_page

    data = {
        "social_media": social_media,
        "request": context["request"],
        "locale_code": locale,
        "page": page,
    }
    return data


@register.inclusion_tag("home/tags/social_media_article.html", takes_context=True)
def social_media_article(context, page=None):
    site = Site.find_for_request(context["request"])
    site_settings = SiteSettings.for_site(site)
    viber = False
    twitter = False
    facebook = False
    whatsapp = False
    telegram = False

    if site_settings:
        facebook = site_settings.facebook_image
        twitter = site_settings.twitter_image
        whatsapp = site_settings.whatsapp_image
        viber = site_settings.viber_image
        telegram = site_settings.telegram_image

    data = {
        "page": page,
        "viber": viber,
        "twitter": twitter,
        "facebook": facebook,
        "whatsapp": whatsapp,
        "telegram": telegram,
        "locale_code": locale,
        "request": context["request"],
    }
    return data
