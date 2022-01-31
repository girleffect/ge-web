import json
from django.core.management.base import BaseCommand
from wagtail.core.models import Locale
from home.models import HomePage
from articles.models import SectionIndexPage

class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('langs.json', 'r', encoding='utf-8') as f:
            langs = json.load(f)
            for lang in langs.keys():
                locale, created = Locale.objects.get_or_create(language_code=langs[lang]["locale"])

        default_home = HomePage.objects.first()
        for locale in Locale.objects.all():
            try:
                home_page = HomePage.objects.get(locale=locale)
            except HomePage.DoesNotExist:
                home_page = HomePage(locale=locale, title=default_home.title, translation_key=default_home.translation_key)
                default_home.get_parent().add_child(instance=home_page)
                home_page.save_revision().publish()
        for home in HomePage.objects.all():
            sip = home.get_children().filter(title="Sections").exists()
            if not sip:
                new_sip = SectionIndexPage(title="Sections")
                home.add_child(instance=new_sip)
                new_sip.save_revision().publish()
