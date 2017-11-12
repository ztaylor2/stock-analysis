"""Views for the Stock Analysis app."""
from pyramid.view import view_config


@view_config(route_name='home', renderer='stock_analysis:templates/mytemplate.jinja2')
def home_view(request):
    """View for listing journal entries."""
    return {}
