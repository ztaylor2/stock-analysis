"""Include routes for stock analysis app."""


def includeme(config):
    """Include routes for stock analysis app."""
    config.add_static_view('static', 'stock_analysis:static')
    config.add_route('home', '/')
