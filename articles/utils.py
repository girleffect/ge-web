from django.core.paginator import Paginator


def paginate(articles, page=1):
    results = Paginator(articles, 10)
    page_number = page
    page_obj = results.get_page(page_number)
    return page_obj
