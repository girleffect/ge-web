from home.utils import get_theme_from_request


def get_theme(request):
    return {"theme": get_theme_from_request(request)}
