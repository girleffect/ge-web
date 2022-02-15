import json

from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand
from wagtail.core.models import Locale
from wagtail.images.models import Image

from articles.models import SectionPage
from home.models import HomePage


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("sections.json", "r", encoding="utf-8") as f:
            sections = json.load(f)
            for section in sections.keys():
                try:
                    locale = Locale.objects.get(
                        language_code=sections[section]["locale"]
                    )
                except MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.WARNING(
                            "Multiple Locales found: "
                            + str(sections[section]["locale"])
                        )
                    )
                except Locale.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            "Locale does not exist: " + str(sections[section]["locale"])
                        )
                    )
                try:
                    home_page = HomePage.objects.get(
                        title__icontains=sections[section]["main_title"], locale=locale
                    )
                except MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.WARNING(
                            "Multiple home pages found: "
                            + str(sections[section]["main_title"])
                        )
                    )
                except HomePage.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            "Home page does not exist: "
                            + str(sections[section]["main_title"])
                        )
                    )
                try:
                    new_section = SectionPage.objects.get(
                        locale=locale,
                        title=sections[section]["title"],
                        site__pk=home_page.site.pk,
                    )
                except MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.WARNING(
                            "Multiple section pages found: "
                            + str(sections[section]["title"])
                        )
                    )
                except SectionPage.DoesNotExist:
                    new_section = SectionPage(
                        locale=locale,
                        title=sections[section]["title"],
                        slug=sections[section]["slug"],
                    )
                    if "image_filename" in sections[section].keys():
                        if Image.objects.filter(
                            filename=sections[section]["image_filename"]
                        ).exists():
                            new_section.image = Image.objects.get(
                                sections[section]["image_filename"]
                            )
                    if "translation_pks" in sections[section].keys():
                        trans_pks = sections[section]["translation_pks"]
                        trans_slug = sections[str(trans_pks[0])]["slug"]
                        trans_locale = sections[str(trans_pks[0])]["locale"]
                        try:
                            trans_section = SectionPage.objects.get(
                                slug=trans_slug,
                                locale__language_code=trans_locale,
                                site__pk=home_page.site.pk,
                            )
                            new_section.translation_key = trans_section.translation_key
                        except SectionPage.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    "Translation does not exist: " + str(trans_slug)
                                )
                            )
                    if "section_parent_pk" in sections[section].keys():
                        parent_slug = sections[sections[section]["section_parent_pk"]][
                            "slug"
                        ]
                        parent_locale = sections[
                            sections[section]["section_parent_pk"]
                        ]["locale"]
                        parent = SectionPage.objects.get(
                            slug=parent_slug,
                            locale__language_code=parent_locale,
                            site=home_page.site,
                        )
                    else:
                        parent = home_page
                    parent.add_child(instance=new_section)
                    if sections[section]["is_live"]:
                        new_section.save_revision().publish()
                    else:
                        new_section.save_revision()
