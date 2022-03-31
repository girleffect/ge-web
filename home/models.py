from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel

from articles.models import ArticlePage, SectionIndexPage, SectionPage
from forms.models import FormPage
from home.blocks import BannerBlock
from home.themes import THEME_CHOICES

from wagtail.admin.edit_handlers import (  # isort:skip
    FieldPanel,
    MultiFieldPanel,
    StreamFieldPanel,
)


class HomePage(Page):
    subpage_types = [
        "articles.SectionIndexPage",
        "articles.FooterIndexPage",
        "forms.FormsIndexPage",
        "profiles.SecurityQuestionIndexPage",
    ]
    banners = StreamField(
        [
            ("banner", BannerBlock()),
        ],
        blank=True,
        null=True,
    )
    theme = models.CharField(
        verbose_name=_("theme"),
        max_length=100,
        choices=THEME_CHOICES,
        blank=True,
        null=True,
        db_index=True,
    )

    featured_articles = models.TextField(
        default=15,
        null=True,
        blank=True,
        help_text=_("The number of featured articles on the Home Page. Default is 15"),
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("banners"),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel("theme"),
        FieldPanel("featured_articles"),
    ]

    def get_context(self, request):
        # Update context to seperate sectionpages and tag index
        context = super().get_context(request)
        section_index = SectionIndexPage.objects.descendant_of(self).live().first()
        context["section_index"] = section_index

        sections = SectionPage.objects.child_of(section_index).live()
        context["sections"] = sections

        forms = FormPage.objects.descendant_of(self).live()
        context["forms"] = forms

        try:
            number_featured = int(self.featured_articles)
        except ValueError:
            number_featured = 15

        articlepages = (
            ArticlePage.objects.filter(feature_in_homepage=True)
            .live()
            .descendant_of(section_index)[:number_featured]
        )

        if len(articlepages) < number_featured:
            number_needed = number_featured - len(articlepages)
            articlepages = articlepages | (
                ArticlePage.objects.filter(feature_in_homepage=False)
                .live()
                .descendant_of(section_index)
                .order_by("-last_published_at")[:number_needed]
            )
        for article in articlepages:
            # save() is not being used here intentionally to only temporarily set
            # articles as featured for this request
            article.feature_in_homepage = True

        context["articlepages"] = articlepages

        articlepages_in_menu = (
            ArticlePage.objects.live().in_menu().descendant_of(section_index)
        )
        context["articlepages_in_menu"] = articlepages_in_menu

        return context


class SocialMediaLinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    link = blocks.CharBlock(required=True)
    image = ImageChooserBlock()


@register_setting
class SiteSettings(BaseSetting):
    fb_analytics_app_id = models.CharField(
        verbose_name=_("Facebook Analytics App ID"),
        max_length=25,
        null=True,
        blank=True,
        help_text=_("The tracking ID to be used to view Facebook Analytics"),
    )
    fb_enable_chat_bot = models.BooleanField(
        default=False, help_text="Activate chat-bot for facebook messenger."
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
            ("social_media_site", SocialMediaLinkBlock()),
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
    moderator_reply_name = models.CharField(
        verbose_name=_("moderator"),
        max_length=100,
        default="BigSis",
        null=True,
        blank=True,
        help_text=_(
            "The name that will appear on the moderator comment reply. Default is BigSis"
        ),
    )

    commenting_switch = models.BooleanField(
        verbose_name=_("commenting"),
        default=True,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("fb_analytics_app_id"),
                FieldPanel("fb_enable_chat_bot"),
            ],
            heading="Facebook Settings",
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
        FieldPanel("moderator_reply_name"),
        FieldPanel("commenting_switch"),
    ]
