import json

from django.core.management.base import BaseCommand
from wagtail.core.models import Locale
from wagtail.images.models import Image

from articles.models import SectionPage
from home.models import HomePage


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("sections.json", "r", encoding="utf-8") as f:
            sections = json.load(f)
            SectionPage.objects.all().delete()
            for section in sections.keys():
                locale = Locale.objects.get(language_code=sections[section]["locale"])
                try:
                    new_section = SectionPage.objects.get(
                        locale=locale, title=sections[section]["title"]
                    )
                except SectionPage.DoesNotExist:
                    new_section = SectionPage(
                        locale=locale,
                        title=sections[section]["title"],
                        slug=sections[section]["slug"],
                    )
                    if sections[section]["image_name"]:
                        if Image.objects.filter(title="image_name").exists():
                            new_section.image = Image.objects.get(title="image_name")
                    if "translation_pks" in sections[section].keys():
                        trans_pks = sections[section]["translation_pks"]
                        trans_slug = sections[str(trans_pks[0])]["slug"]
                        trans_locale = sections[str(trans_pks[0])]["locale"]
                        try:
                            trans_section = SectionPage.objects.get(
                                slug=trans_slug, locale__language_code=trans_locale
                            )
                            new_section.translation_key = trans_section.translation_key
                        except:
                            pass
                    if "section_parent_pk" in sections[section].keys():
                        parent_slug = sections[sections[section]["section_parent_pk"]][
                            "slug"
                        ]
                        parent_locale = sections[
                            sections[section]["section_parent_pk"]
                        ]["locale"]
                        parent = SectionPage.objects.get(
                            slug=parent_slug, locale__language_code=parent_locale
                        )
                    else:
                        parent = (
                            HomePage.objects.get(locale=locale)
                            .get_children()
                            .filter(title="Sections")
                            .first()
                        )
                    parent.add_child(instance=new_section)
                    new_section.save_revision().publish()
