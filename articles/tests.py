from django.test import TestCase, RequestFactory
from home.models import HomePage
from articles.models import SectionPage, SectionIndexPage, ArticlePage
from wagtail.core.models import Site
from django.contrib.contenttypes.models import ContentType
from wagtail.core.models import Page
from .templatetags.article_tags import get_next_article, breadcrumbs


class ArticlesTestCaseMixin(object):
    def mk_root(self):
        page_content_type, created = ContentType.objects.get_or_create(
            model="page", app_label="wagtailcore"
        )
        self.root, _ = Page.objects.get_or_create(
            title="Root",
            slug="root",
            content_type=page_content_type,
            path="0001",
            depth=1,
            numchild=1,
            url_path="/",
        )

    def setup_cms(self):
        self.mk_root()
        self.factory = RequestFactory()
        # Create a new homepage
        self.main = HomePage.objects.first()

        # Create index page
        self.index = SectionIndexPage(title="Sections", slug="security-questions")
        self.main.add_child(instance=self.index)
        self.index.save_revision().publish()
        self.section = SectionPage(title="section1", slug="section-1")
        self.index.add_child(instance=self.section)
        self.section.save_revision().publish()
        self.article = ArticlePage(title="How old are you?", slug="how-old-are-you")
        self.section.add_child(instance=self.article)
        self.article.save_revision().publish()
        self.site = Site.objects.get(is_default_site=True)


class TestTemplateTags(TestCase, ArticlesTestCaseMixin):
    def setUp(self):
        self.setup_cms()

    def test_breadcrumbs(self):
        request = self.factory.get(self.article.url)
        context = {"locale_code": "en", "request": request, "self": self.article}
        ancestors = breadcrumbs(context)["ancestors"]
        # it should only return 2
        self.assertEquals(ancestors.count(), 2)
        # it should not include section index page
        for ancestor in ancestors:
            self.assertTrue(ancestor.pk in [self.article.pk, self.section.pk])

    def test_get_next_article(self):
        request = self.factory.get("/")
        context = {"locale_code": "en", "request": request}

        # it should return None if there is only 1 article
        self.assertEquals(get_next_article(context, self.article), None)

        self.article2 = ArticlePage(title="How big are you?", slug="how-big-are-you")
        self.section.add_child(instance=self.article2)
        self.article2.save_revision().publish()
        self.article2.unpublish()
        # it should return None if there is only 1 article live
        self.assertEquals(get_next_article(context, self.article), None)

        # it should return None if the next sibling is not an article
        self.assertEquals(get_next_article(context, self.article2), None)

        self.article3 = ArticlePage(
            title="How great are you?", slug="how-great-are-you"
        )
        self.section.add_child(instance=self.article3)
        self.article3.save_revision().publish()
        # it should return article 3
        self.assertEquals(get_next_article(context, self.article).pk, self.article3.pk)
