"""Include routes for stock analysis app."""


def includeme(config):
    """Include routes for stock analysis app."""
    config.add_static_view('static', 'stock_analysis:static')
    config.add_route('home', '/')
    config.add_route('portfolio', '/portfolio')
    config.add_route('detail', '/detail')
    config.add_route('logout', '/logout')
    config.add_route('login', '/login')
    config.add_route('register', '/register')
