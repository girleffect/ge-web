import json
from django.core.management.base import BaseCommand
from articles.models import ArticlePage, SectionPage
from wagtail.admin.rich_text.converters.editor_html import EditorHTMLConverter
from wagtail.core.rich_text import RichText
from wagtail.core.models import Locale


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('articles.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
            ArticlePage.objects.all().delete()
            for article in articles.keys():
                locale = Locale.objects.get(language_code=articles[article]["locale"])
                body_raw = EditorHTMLConverter().from_database_format(articles[article]["body"])
                body = [("paragraph", RichText(body_raw))]
                article_page = ArticlePage(title=articles[article]["title"], slug=articles[article]["slug"], subtitle=articles[article]["subtitle"], body=body, locale=locale)
                if "translation_pks" in articles[article].keys():
                    trans_pks = articles[article]["translation_pks"]
                    trans_slug = articles[str(trans_pks[0])]["slug"]
                    trans_locale = articles[str(trans_pks[0])]["locale"]
                    try:
                        trans_article = ArticlePage.objects.get(slug=trans_slug, locale__language_code=trans_locale)
                        article_page.translation_key = trans_article.translation_key
                    except:
                        pass
                if "parent_section_slug" in articles[article].keys():
                    parent = SectionPage.objects.get(slug=articles[article]["parent_section_slug"], locale=locale)
                    parent.add_child(instance=article_page)
                    article_page.save_revision().publish()
