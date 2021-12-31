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


class SectionPage(Page):
    subpage_types = [
        "articles.ArticlePage",
        "articles.SectionPage",
    ]
    parent_page_type = ["articles.SectionPage", "articles.SectionIndexPage"]
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    css_color = models.TextField(
        default="",
        null=True,
        blank=True,
        help_text=_("CSS color that should be applied to this section"),
    )
    content_panels = Page.content_panels + [
        ImageChooserPanel("image"),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel("css_color"),
    ]

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        articlepages = self.get_children().live().order_by("-first_published_at")
        context["articlepages"] = articlepages
        return context

    def sections(self):
        # Update context to seperate sectionpages
        return self.get_parent().get_children().live()


class ArticlePageTag(TaggedItemBase):
    content_object = ParentalKey(
        "ArticlePage", on_delete=models.CASCADE, related_name="tagged_items"
    )


class ArticlePage(Page):
    parent_page_type = [
        "articles.SectionPage",
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

    def article_parent(self):
        # Update context to seperate sectionpages
        return self.get_parent()
    
    def article_sections(self):
        # Update context to seperate sectionpages
        return self.get_parent().get_parent().get_children().live()


class SectionIndexPage(Page):
    subpage_types = ["SectionPage"]


class FooterIndexPage(Page):
    subpage_types = ["FooterPage"]


class FooterPage(ArticlePage):
    parent_page_types = ["FooterIndexPage"]
    subpage_types = []
