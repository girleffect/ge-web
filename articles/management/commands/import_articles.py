import json

from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand
from wagtail.admin.rich_text.converters.editor_html import EditorHTMLConverter
from wagtail.core.models import Locale
from wagtail.core.rich_text import RichText
from wagtail.images.models import Image

from articles.models import ArticlePage, SectionPage
from home.models import HomePage


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("articles.json", "r", encoding="utf-8") as f:
            articles = json.load(f)
            for article in articles.keys():
                try:
                    locale = Locale.objects.get(
                        language_code=articles[article]["locale"]
                    )
                except MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.WARNING(
                            "Multiple locales found: "
                            + str(articles[article]["locale"])
                        )
                    )
                except Locale.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            "Locale does not exist: " + str(articles[article]["locale"])
                        )
                    )
                    pass
                try:
                    home_page = HomePage.objects.get(
                        title__icontains=articles[article]["main_title"], locale=locale
                    )
                except MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.WARNING(
                            "Multiple home pages found: "
                            + str(articles[article]["main_title"])
                        )
                    )
                except HomePage.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            "Home page does not exist: "
                            + str(articles[article]["main_title"])
                        )
                    )
                    pass
                body_raw = EditorHTMLConverter().from_database_format(
                    articles[article]["body"]
                )
                body = [("paragraph", RichText(body_raw))]
                if not ArticlePage.objects.filter(
                    title=articles[article]["title"],
                    slug=articles[article]["slug"],
                    subtitle=articles[article]["subtitle"],
                    locale=locale,
                    site__pk=home_page.site.pk,
                ).exists():
                    article_page = ArticlePage(
                        title=articles[article]["title"],
                        slug=articles[article]["slug"],
                        subtitle=articles[article]["subtitle"],
                        body=body,
                        locale=locale,
                    )
                    if "image_filename" in articles[article].keys():
                        if Image.objects.filter(
                            filename=articles[article]["image_filename"]
                        ).exists():
                            article_page.image = Image.objects.get(
                                filename=articles[article]["image_filename"]
                            )

                    if "translation_pks" in articles[article].keys():
                        trans_pks = articles[article]["translation_pks"]
                        trans_slug = articles[str(trans_pks[0])]["slug"]
                        trans_locale = articles[str(trans_pks[0])]["locale"]
                        try:
                            trans_article = ArticlePage.objects.get(
                                slug=trans_slug, locale__language_code=trans_locale
                            )
                            article_page.translation_key = trans_article.translation_key
                        except ArticlePage.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    "Translation does not exist: " + str(trans_slug)
                                )
                            )
                    if "parent_section_slug" in articles[article].keys():
                        try:
                            parent = SectionPage.objects.get(
                                slug=articles[article]["parent_section_slug"],
                                locale=locale,
                                site__pk=home_page.site.pk,
                            )
                            parent.add_child(instance=article_page)
                        except MultipleObjectsReturned:
                            self.stdout.write(
                                self.style.WARNING(
                                    "Multiple Section Parents found: "
                                    + str(articles[article]["parent_section_slug"])
                                )
                            )
                        except SectionPage.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    "Section Parent does not exist: "
                                    + str(articles[article]["parent_section_slug"])
                                )
                            )
                        if articles[article]["is_live"]:
                            article_page.save_revision().publish()
                        else:
                            article_page.save_revision()
