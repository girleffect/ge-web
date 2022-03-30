from django import template
from wagtail.core.models import Site

from home.models import SiteSettings
from home.utils import get_moderator_reply_name_from_request

register = template.Library()


@register.inclusion_tag("home/tags/social_media_footer.html", takes_context=True)
def social_media_footer(context, page=None):
    site = Site.find_for_request(context["request"])
    social_media = SiteSettings.for_site(site).social_media_links_on_footer_page

    data = {
        "social_media": social_media,
        "request": context["request"],
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
        "request": context["request"],
    }
    return data


@register.filter(name="field_type")
def field_type(field):
    return field.field.widget.__class__.__name__


@register.simple_tag(takes_context=True)
def get_moderator_reply_name(context):
    """
    Returns the moderator_reply_name for the current request (retrieved from
    the site root).
    """
    request = context["request"]
    return get_moderator_reply_name_from_request(request)
