"""404 Not Found view."""

from pyramid.view import notfound_view_config


@notfound_view_config(renderer='stock_analysis:templates/404.jinja2')
def notfound_view(request):
    """Not found."""
    request.response.status = 404  # pragma: no cover
    return {}  # pragma: no cover
