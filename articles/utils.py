from django.core.paginator import Paginator


def paginate(articles, page=1):
    return Paginator(articles, 10).get_page(page)


def filesizeformat(bytes):
    """
    Formats the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc).
    """
    try:
        bytes = float(bytes)
    except (TypeError,ValueError,UnicodeDecodeError):
        return u"0 bytes"

    if bytes < 1024:
        return ungettext("%(size)d byte", "%(size)d bytes", bytes) % {'size': bytes}
    if bytes < 1024 * 1024:
        return ugettext("%.1f KB") % (bytes / 1024)
    if bytes < 1024 * 1024 * 1024:
        return ugettext("%.1f MB") % (bytes / (1024 * 1024))
    return ugettext("%.1f GB") % (bytes / (1024 * 1024 * 1024))
filesizeformat.is_safe = True 
