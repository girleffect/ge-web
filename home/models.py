from django.db import models

from wagtail.core.models import Page

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.core.fields import StreamField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.search import index
from django.utils.translation import gettext_lazy as _
from home.themes import THEME_CHOICES
from articles.models import SectionPage
from forms.models import FormPage


class HomePage(Page):
    subpage_types = [
        "articles.SectionIndexPage",
        "articles.FooterIndexPage",
        "forms.FormsIndexPage",
    ]

    theme = models.CharField(
        verbose_name=_("theme"),
        max_length=100,
        choices=THEME_CHOICES,
        blank=True,
        null=True,
        db_index=True,
    )

    settings_panels = Page.settings_panels + [
        FieldPanel("theme"),
    ]

    def get_context(self, request):
        # Update context to seperate sectionpages and tag index
        context = super().get_context(request)
        sections = SectionPage.objects.descendant_of(self).live()
        context["sections"] = sections

        forms = FormPage.objects.descendant_of(self).live()
        context["forms"] = forms

        return context


@register_setting
class SiteSettings(BaseSetting):
    fb_analytics_app_id = models.CharField(
        verbose_name=_("Facebook Analytics App ID"),
        max_length=25,
        null=True,
        blank=True,
        help_text=_("The tracking ID to be used to view Facebook Analytics"),
    )
    ga_tag_manager = models.CharField(
        verbose_name=_("Local GA Tag Manager"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Local GA Tag Manager tracking code (e.g GTM-XXX) to be used to "
            "view analytics on this site only"
        ),
    )
    global_ga_tag_manager = models.CharField(
        verbose_name=_("Global GA Tag Manager"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Global GA Tag Manager tracking code (e.g GTM-XXX) to be used"
            " to view analytics on more than one site globally"
        ),
    )
    google_search_console = models.CharField(
        verbose_name=_("Google Search Console"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("The Google Search Console verification code"),
    )
    social_media_links_on_footer_page = StreamField(
        [
            ("social_media_site", blocks.URLBlock()),
        ],
        null=True,
        blank=True,
    )
    facebook_sharing = models.BooleanField(
        default=False,
        verbose_name="Facebook",
        help_text="Enable this field to allow for sharing to Facebook.",
    )
    facebook_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    twitter_sharing = models.BooleanField(
        default=False,
        verbose_name="Twitter",
        help_text="Enable this field to allow for sharing to Twitter.",
    )
    twitter_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    whatsapp_sharing = models.BooleanField(
        default=False,
        verbose_name="Whatsapp",
        help_text="Enable this field to allow for sharing to Whatsapp.",
    )
    whatsapp_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    viber_sharing = models.BooleanField(
        default=False,
        verbose_name="Viber",
        help_text="Enable this field to allow for sharing to Viber.",
    )
    viber_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    telegram_sharing = models.BooleanField(
        default=False,
        verbose_name="Telegram",
        help_text="Enable this field to allow for sharing to Telegram.",
    )
    telegram_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("fb_analytics_app_id"),
            ],
            heading="Facebook Analytics Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel("ga_tag_manager"),
                FieldPanel("global_ga_tag_manager"),
            ],
            heading="GA Tag Manager Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel("google_search_console"),
            ],
            heading="Google Search Console Verification Code",
        ),
        MultiFieldPanel(
            [
                MultiFieldPanel(
                    [
                        StreamFieldPanel("social_media_links_on_footer_page"),
                    ],
                    heading="Social Media Footer Page",
                ),
            ],
            heading="Social Media Footer Page Links",
        ),
        MultiFieldPanel(
            [
                FieldPanel("facebook_sharing"),
                ImageChooserPanel("facebook_image"),
                FieldPanel("twitter_sharing"),
                ImageChooserPanel("twitter_image"),
                FieldPanel("whatsapp_sharing"),
                ImageChooserPanel("whatsapp_image"),
                FieldPanel("viber_sharing"),
                ImageChooserPanel("viber_image"),
                FieldPanel("telegram_sharing"),
                ImageChooserPanel("telegram_image"),
            ],
            heading="Social Media Article Sharing Buttons",
        ),
    ]
