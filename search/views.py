from django.shortcuts import render
from django.core.paginator import Paginator
from articles.models import ArticlePage
from wagtail.search.models import Query


def search(request):
    search_query = request.GET.get('query', None)
    if search_query:
        site = Site.find_for_request(request)
        results = ArticlePage.objects.live().descendant_of(site.root_page).search(search_query)
        search_results = Paginator(results, 10)
        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()
    else:
        search_results = ArticlePage.objects.none()

    # Render template
    page_number = request.GET.get('page', '1')
    page_obj = search_results.get_page(page_number)
    return render(request, 'search_results.html', {
        'search_query': search_query,
        'search_results': page_obj,
    })
