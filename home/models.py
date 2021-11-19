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


class HomePage(Page):
    subpage_types = ["SectionPage"]

    def get_context(self, request):
        # Update context to seperate sectionpages and tag index
        context = super().get_context(request)
        sections = SectionPage.objects.child_of(self).live()
        context["sections"] = sections

        return context


class SectionPage(Page):
    subpage_types = [
        "ArticlePage",
        "SectionPage",
    ]
    parent_page_type = ["SectionPage", "HomePage"]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        articlepages = self.get_children().live().order_by("-first_published_at")
        context["articlepages"] = articlepages
        return context


class ArticlePageTag(TaggedItemBase):
    content_object = ParentalKey(
        "ArticlePage", on_delete=models.CASCADE, related_name="tagged_items"
    )


class ArticlePage(Page):
    parent_page_type = [
        "SectionPage",
    ]

    # general page attributes
    tags = ClusterTaggableManager(through=ArticlePageTag, blank=True)

    # Web page setup
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    body = StreamField(
        [
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        blank=True,
        null=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        StreamFieldPanel("body"),
        FieldPanel("tags"),
    ]
    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.SearchField("subtitle"),
    ]


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
