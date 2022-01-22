from django.conf import settings
from home.themes import THEME_CHOICES


def compress_settings(request):
    return {"STATIC_URL": settings.STATIC_URL}
