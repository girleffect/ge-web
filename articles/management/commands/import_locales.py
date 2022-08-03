import json

from django.core.management.base import BaseCommand
from wagtail.core.models import Locale


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("langs.json", "r", encoding="utf-8") as f:
            langs = json.load(f)
            for lang in langs.keys():
                locale, created = Locale.objects.get_or_create(
                    language_code=langs[lang]["locale"]
                )
