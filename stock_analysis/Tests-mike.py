"""Tests for the Stock Analysis app."""

from __future__ import unicode_literals
from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPBadRequest
from datetime import datetime
import os
import pytest


""" UNIT TESTS FOR MODELS """


def test_(db_session):
    """Test that Portfolio constructed when stock is entered."""
    from stock_analysis.models import Portfolio
    assert len(db_session.query(Portfolio).all()) == 0
    stock = Sample_stock(
        company='Yahoo',
        exchange='NYSE',
        ticker='YHOO',
        current='18.55',
        growth='.50',
        open='18.05',
        high='18.95',
        low='18.05'
    )
    db_session.add(stock)
    assert len(db_session.query(Portfolio).all()) == 1


def test_to_dict_puts_all_properties_in_a_dictionary(test_entry):
    """Test that all properties of a stock are in to_dict dictionary."""
    stock_detail = test_entry.to_dict()
    assert all(prop in stock_detail for prop in ['company', 'exchange',
                                                 'ticker', 'current', 'growth',
                                                 'open', 'high', 'low'])


def test_to_html_dict_puts_all_properties_in_a_dictionary(test_entry):
    """Test that all properties of a stock are in to_html_dict dictionary."""
    stock_detail = test_entry.to_html_dict()
    assert all(prop in stock_detail for prop in ['company', 'exchange',
                                                 'ticker', 'current', 'growth',
                                                 'open', 'high', 'low'])

""" UNIT TESTS FOR VIEW FUNCTIONS """


def test_portfolio_view_returns_list(dummy_request, add_stocks):
    """Test that the Portfolio view function returns a list of stocks."""
    from stock_analysis.views.default import portfolio_view
    response = portfolio_view(dummy_request)
    assert 'stocks' in response
    assert isinstance(response['stocks'], list)


def test_portfolio_view_returns_stocks_in_list(dummy_request, add_stocks):
    """Test that Portfolio view function returns entries as dicitonaries."""
    from stock_analysis.views.default import portfolio_view
    response = portfolio_view(dummy_request)
    assert add_stocks[0].to_html_dict() in response['stocks']


def test_portfolio_view_returns_all_stocks_in_db(dummy_request, add_stocks):
    """Test that Portfolio view function returns all entries in database."""
    from stock_analysis.views.default import portfolio_view
    from stock_analysis.models import Portfolio
    response = portfolio_view(dummy_request)
    query = dummy_request.dbsession.query(Portfolio)
    assert len(response['stocks']) == query.count()


def test_detail_view_returns_one_entry_detail(dummy_request, add_stocks):
    """Test that the detail view function returns the data of one entry."""
    from stock_analysis.views.default import detail_view
    dummy_request.matchdict['id'] = 1
    response = detail_view(dummy_request)
    assert add_stocks[0].to_html_dict() == response['stock']


def test_detail_view_returns_correct_stock_detail(dummy_request, add_stocks):
    """Test that the detail view function returns the correct stock data."""
    from stock_analysis.views.default import detail_view
    dummy_request.matchdict['company'] = 'Yahoo'
    response = detail_view(dummy_request)
    assert response['stock']['company'] == 'Yahoo'


def test_detail_view_raises_httpnotfound_if_not_found(dummy_request, add_stocks):
    """Test that detail_view raises HTTPNotFound if symbol is not found."""
    from stock_analysis.views.default import detail_view
    dummy_request.matchdict['company'] = 'asdfaasdffrew'
    with pytest.raises(HTTPNotFound):
        detail_view(dummy_request)


def test__get_symbol_returns_proper_stock_data(dummy_request):
    """Test that the _get_stock function returns proper stock data."""
    from stock_analysis.views.default import portfolio_view
    # from stock_analysis.models import Portfolio
    stock_details = {
        'company': 'Yahoo',
        'exchange': 'NYSE',
        'ticker': 'YHOO',
        'current': '18.55',
        'growth': '.50',
        'open': '18.05',
        'high': '18.95',
        'low': '18.05'
    }
    dummy_request.method = 'POST'
    dummy_request.POST = stock_details
    _get_symbol(dummy_request)
    assert dummy_request.dbsession.query(portfolio_view).count() == 1


def test_portfolio_view_post_creates_new_entry_with_given_info(dummy_request):
    """Test that new stock created uses POST info on portfolio_view POST."""
    from stock_analysis.views.default import portfolio_view
    from stock_analysis.models import Portfolio
    stock_details = {
        'company': 'Yahoo',
        'exchange': 'NYSE',
        'ticker': 'YHOO',
        'current': '18.55',
        'growth': '.50',
        'open': '18.05',
        'high': '18.95',
        'low': '18.05'
    }
    dummy_request.method = 'POST'
    dummy_request.POST = stock_details
    portfolio_view(dummy_request)
    entry = dummy_request.dbsession.query(Portfolio).get(1)
    assert entry.company == stock_details['company']
    assert entry.exchange == stock_details['exchange']
    assert entry.ticker == stock_details['ticker']
    assert entry.current == stock_details['current']
    assert entry.growth == stock_details['growth']
    assert entry.open == stock_details['open']
    assert entry.high == stock_details['high']
    assert entry.low == stock_details['low']


def test_portfolio_view_post_has_302_status_code(dummy_request):
    """Test that portfolio_view POST has 302 status code."""
    from stock_analysis.views.default import portfolio_view
    stock_details = {
        'company': 'Yahoo',
        'exchange': 'NYSE',
        'ticker': 'YHOO',
        'current': '18.55',
        'growth': '.50',
        'open': '18.05',
        'high': '18.95',
        'low': '18.05'
    }
    dummy_request.method = 'POST'
    dummy_request.POST = stock_details
    response = portfolio_view(dummy_request)
    assert response.status_code == 302


def test_portfolio_view_post_redirects_to_portfolio_view_with_httpfound(dummy_request):
    """Test that portfolio_view POST redirects to portfolio view with httpfound."""
    from stock_analysis.views.default import portfolio_view
    stock_details = {
        'company': 'Yahoo',
        'exchange': 'NYSE',
        'ticker': 'YHOO',
        'current': '18.55',
        'growth': '.50',
        'open': '18.05',
        'high': '18.95',
        'low': '18.05'
    }
    dummy_request.method = 'POST'
    dummy_request.POST = stock_details
    response = portfolio_view(dummy_request)
    assert isinstance(response, HTTPFound)
    assert response.location == dummy_request.route_url('home')


def test_portfolio_view_post_incompelete_data_is_bad_request(dummy_request):
    """Test that portfolio_view POST with incomplete data is invalid."""
    from stock_analysis.views.default import portfolio_view
    stock_details = {
        'company': 'Yahoo',
        'exchange': 'NYSE',
        'ticker': 'YHOO',
        'current': '18.55',
        'growth': '.50',
        'open': '18.05',
        'high': '18.95',
        'low': '18.05'
    }
    dummy_request.method = 'POST'
    dummy_request.POST = stock_details
    with pytest.raises(HTTPBadRequest):
        portfolio_view(dummy_request)


def test_login_returns_only_home_page_for_unauthenticated_user(dummy_request):
    """Test that the login function returns only home page for unauth GET."""
    from stock_analysis.views.default import login_view
    response = login_view(dummy_request)
    assert 'get-started' in response
    assert 'Login' == response['Password']


def test_login_post_incomplete_data_is_bad_request(dummy_request, username, password):
    """Test that login POST with incomplete data is invalid."""
    from stock_analysis.views.default import login_view
    data = {
        'username': 'name'
    }
    dummy_request.method = 'POST'
    dummy_request.POST = data
    with pytest.raises(HTTPBadRequest):
        login_view(dummy_request)


def test_login_post_incorrect_data_returns_dict_with_error(dummy_request):
    """Test that login POST with incorrect data is invalid."""
    from stock_analysis.views.default import login_view
    data = {
        'username': 'name',
        'password': 'pass'
    }
    dummy_request.method = 'POST'
    dummy_request.POST = data
    response = login_view(dummy_request)
    assert 'error' in response
    assert 'The username and/or password are incorrect.' == response['error']
