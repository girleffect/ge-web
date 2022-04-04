from django.core.paginator import Paginator


def paginate(articles, page=1):
    return Paginator(articles, 10).get_page(page)
