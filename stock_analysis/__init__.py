"""Initialization of the Stock Analysis application."""
import os
from pyramid.config import Configurator


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    settings['sqlalchemy.url'] = os.environ.get('DATABASE_URL', '')
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    # config.include('.models')
    config.include('.security')
    config.include('.routes')
    config.scan()
    return config.make_wsgi_app()
