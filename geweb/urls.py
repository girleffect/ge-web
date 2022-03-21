from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from comments import urls as comments_urls
from home import views
from profiles import urls as profile_urls
from search import views as search_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("profiles/", include(profile_urls), name="profiles"),
    path("comments/", include(comments_urls), name="comments"),
    path("", include("social_django.urls", namespace="social")),
    path("health/", views.health, name="health"),
    path("i18n/", include("django.conf.urls.i18n")),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path("search/", search_views.search, name="search"),
    path("", include(wagtail_urls)),
)
