import json

from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand
from wagtail.core.models import Locale, Site

from articles.models import SectionIndexPage
from home.models import HomePage


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("mains.json", "r", encoding="utf-8") as f:
            mains = json.load(f)
            for main in mains.keys():
                try:
                    locale = Locale.objects.get(language_code=mains[main]["locale"])
                except MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.WARNING(
                            "Multiple locales found: " + str(mains[main]["locale"])
                        )
                    )
                    pass
                except Locale.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            "Locale does not exist: " + str(mains[main]["locale"])
                        )
                    )
                    pass
                try:
                    main, created = HomePage.objects.get_or_create(
                        title=mains[main]["title"], locale=locale
                    )
                except MultipleObjectsReturned:
                    self.stdout.write(
                        self.style.WARNING(
                            "Multiple home pages found: " + str(mains[main]["title"])
                        )
                    )
                    pass
                if not Site.objects.filter(root_page=main).exists():
                    Site.objects.create(
                        root_page=main,
                        site_name=main.title,
                        hostname=mains[main]["hostname"],
                        port=mains[main]["port"],
                    )
                sip = main.get_children().filter(title="Sections").exists()
                if not sip:
                    new_sip = SectionIndexPage(title="Sections")
                    main.add_child(instance=new_sip)
                    new_sip.save_revision().publish()
