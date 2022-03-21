from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class BannerBlock(blocks.StructBlock):
    banner_image = ImageChooserBlock(required=False)
    banner_link_page = blocks.PageChooserBlock(required=False)
    banner_external_link = blocks.URLBlock(required=False)

    class Meta:
        icon = "snippet"
