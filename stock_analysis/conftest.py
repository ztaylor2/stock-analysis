"""Fixtures for the pyramid_learning_journal tests."""

from __future__ import unicode_literals
from pyramid import testing
from stock_analysis.models.meta import Base
from stock_analysis.models import Portfolio, User, get_tm_session
from passlib.apps import custom_app_context as pwd_context
import transaction
import os
import pytest


@pytest.fixture
def test_entry():
    """Create a new Entry."""
    stock_sample = {
        'company': 'Yahoo',
        'exchange': 'NYSE',
        'ticker': 'YHOO',
        'current': '18.55',
        'growth': '.50',
        'open': '18.05',
        'high': '18.95',
        'low': '18.05'
    }
    return stock_sample  # FORMERLY == Entry


@pytest.fixture(scope='session')
def configuration(request):
    """Setup a database for testing purposes."""
    config = testing.setUp(settings={
        'sqlalchemy.url': os.environ['TEST_DATABASE_URL']
    })
    config.include('stock_analysis.models')
    config.include('stock_analysis.routes')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture
def db_session(configuration, request):
    """Create a database session for interacting with the test database."""
    SessionFactory = configuration.registry['dbsession_factory']
    session = SessionFactory()
    engine = session.bind
    Base.metadata.create_all(engine)

    def teardown():
        session.transaction.rollback()
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(db_session):
    """Create a dummy GET request with a dbsession."""
    return testing.DummyRequest(dbsession=db_session)


@pytest.fixture
def add_stock(dummy_request, test_stock):  # FORMERLY add_entry
    """Add the first Stock to database."""
    dummy_request.dbsession.add(test_stock)
    return test_stock


@pytest.fixture
def add_stocks(dummy_request, test_stock):  # FORMERLY add_entries
    """Add a Stock to an existing table in the database."""
    dummy_request.dbsession.add_all(test_stocks)
    return test_stocks


@pytest.fixture(scope="session")
def testapp(request):
    """Functional test for app."""
    from webtest import TestApp
    from pyramid.config import Configurator

    def main():
        settings = {
            'sqlalchemy.url': os.environ['TEST_DATABASE_URL']
        }
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('stock_analysis.routes')
        config.include('stock_analysis.models')
        config.include("stock_analysis.security")
        config.scan()
        return config.make_wsgi_app()

    app = main()

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.create_all(bind=engine)

    def tearDown():
        Base.metadata.drop_all(bind=engine)

    request.addfinalizer(tearDown)

    return TestApp(app)


@pytest.fixture(scope='session')
def test_stock_session():
    """Create a list of Stocks to be added to the database."""
    stock_sample = {'username': 'shinners',
                    'stocks': 'YHOO'
                    }
    return stock_sample


@pytest.fixture(scope='session')
def fill_the_db(testapp, test_stock_session):
    """Fill the test database with dummy stocks."""
    SessionFactory = testapp.app.registry['dbsession_factory']
    portfolio = Portfolio(username=test_stock_session['username'], stocks=test_stock_session['stocks'])
    with transaction.manager:
        dbsession = get_tm_session(SessionFactory, transaction.manager)
        dbsession.add(portfolio)

    return dbsession


@pytest.fixture
def empty_the_db(testapp):
    """Tear down the database and add a fresh table."""
    SessionFactory = testapp.app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def testapp_session(testapp, request):
    """Create a session to interact with the database."""
    SessionFactory = testapp.app.registry["dbsession_factory"]
    session = SessionFactory()
    engine = session.bind

    def teardown():
        session.transaction.rollback()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def username():
    """Set the username for testing purposes."""
    os.environ['AUTH_USERNAME'] = 'name'
    return 'name'


@pytest.fixture
def password():
    """Set the password for testing purposes."""
    os.environ['AUTH_PASSWORD'] = pwd_context.hash('password')
    return 'password'
