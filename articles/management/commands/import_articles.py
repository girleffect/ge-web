import json
import boto3
from django.core.management.base import BaseCommand
from articles.models import ArticlePage, SectionPage
from wagtail.admin.rich_text.converters.editor_html import EditorHTMLConverter
from wagtail.core.rich_text import RichText
from wagtail.core.models import Locale
from wagtail.images.models import Image


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("articles.json", "r", encoding="utf-8") as f:
            s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            articles = json.load(f)
            ArticlePage.objects.all().delete()
            for article in articles.keys():
                locale = Locale.objects.get(language_code=articles[article]["locale"])
                body_raw = EditorHTMLConverter().from_database_format(
                    articles[article]["body"]
                )
                body = [("paragraph", RichText(body_raw))]
                article_page = ArticlePage(
                    title=articles[article]["title"],
                    slug=articles[article]["slug"],
                    subtitle=articles[article]["subtitle"],
                    body=body,
                    locale=locale,
                )
                if "image_name" in articles[article].keys():
                    if Image.objects.filter(title="image_name").exists():
                        article_page.image = Image.objects.get(title="image_name")
                    else:
                        img_file = s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, articles[article]["image_name"],  articles[article]["image_name"])
                        img_obj = Image.objects.create(title=articles[article]["image_name"], file=img_file, width=width, height=height)
                        article_page.image = img_obj

                if "translation_pks" in articles[article].keys():
                    trans_pks = articles[article]["translation_pks"]
                    trans_slug = articles[str(trans_pks[0])]["slug"]
                    trans_locale = articles[str(trans_pks[0])]["locale"]
                    try:
                        trans_article = ArticlePage.objects.get(
                            slug=trans_slug, locale__language_code=trans_locale
                        )
                        article_page.translation_key = trans_article.translation_key
                    except:
                        pass
                if "parent_section_slug" in articles[article].keys():
                    parent = SectionPage.objects.get(
                        slug=articles[article]["parent_section_slug"], locale=locale
                    )
                    parent.add_child(instance=article_page)
                    article_page.save_revision().publish()
