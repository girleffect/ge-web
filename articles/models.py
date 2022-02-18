from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from .utils import paginate

from wagtail.admin.edit_handlers import (  # isort:skip
    FieldPanel,
    MultiFieldPanel,
    StreamFieldPanel,
)


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
        page = request.GET.get("page", 1)
        articlepages = self.get_children().live().order_by("-first_published_at")
        articlepages = paginate(articlepages, page)
        context["articlepages"] = articlepages
        return context


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
    feature_in_homepage = models.BooleanField(
        default=False,
        help_text=_(
            "Whether this article should appear with other featured articles"
            " at the top of the home page"
        ),
    )

    # Web page setup
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
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
        ImageChooserPanel("image"),
        StreamFieldPanel("body"),
        FieldPanel("tags"),
    ]
    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.SearchField("subtitle"),
    ]
    promote_panels = Page.promote_panels + [
        MultiFieldPanel([FieldPanel("feature_in_homepage")], "Featured in Homepage"),
    ]


class SectionIndexPage(Page):
    subpage_types = ["SectionPage"]


class FooterIndexPage(Page):
    subpage_types = ["FooterPage"]


class FooterPage(ArticlePage):
    parent_page_types = ["FooterIndexPage"]
    subpage_types = []
