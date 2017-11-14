"""Include routes for stock analysis app."""


def includeme(config):
    """Include routes for stock analysis app."""
    config.add_static_view('static', 'stock_analysis:static')
    config.add_route('home', '/')
    config.add_route('process_symbol', '/symbol')
    config.add_route('portfolio', '/portfolio')
    config.add_route('detail', '/detail')
    config.add_route('logout', '/logout')

