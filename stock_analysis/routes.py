"""Include routes for stock analysis app."""


def includeme(config):
    """Include routes for stock analysis app."""
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
