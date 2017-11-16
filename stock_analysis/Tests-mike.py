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


def test_login_post_correct_data_returns_302_status_code(dummy_request, username, password):
    """Test that login POST with correct data gets 302 status code."""
    from stock_analysis.views.default import login_view
    data = {
        'username': username,
        'password': password
    }
    dummy_request.method = 'POST'
    dummy_request.POST = data
    response = login_view(dummy_request)
    assert response.status_code == 302


def test_login_post_correct_data_redirects_to_home_with_httpfound(dummy_request, username, password):
    """Test that login POST with correct data redirects to home page."""
    from stock_analysis.views.default import login_view
    data = {
        'username': username,
        'password': password
    }
    dummy_request.method = 'POST'
    dummy_request.POST = data
    response = login_view(dummy_request)
    assert isinstance(response, HTTPFound)
    assert response.location == dummy_request.route_url('home')


def test_logout_returns_302_status_code(dummy_request):
    """Test that logout gets 302 status code."""
    from stock_analysis.views.default import logout
    response = logout(dummy_request)
    assert response.status_code == 302


def test_logout_redirects_to_home_with_httpfound(dummy_request):
    """Test that logout redirects to home page."""
    from stock_analysis.views.default import logout
    response = logout(dummy_request)
    assert isinstance(response, HTTPFound)
    assert response.location == dummy_request.route_url('home')


""" FUNCTIONAL TESTS FOR ROUTES """


def test_home_route_gets_200_status_code(testapp, fill_the_db):
    """Test that the home route gets 200 status code for unauth user."""
    response = testapp.get("/")
    assert response.status_code == 200


def test_home_route_has_login_option(testapp):
    """Test that the home route has a login option."""
    response = testapp.get("/")
    assert len(response.html.find_all('li', 'nav-item')) == 2
    assert 'Login' in str(response.html.find_all('li', 'nav-item')[1])


def test_detail_route_for_valid_id_gets_200_status_code(testapp):
    """Test that a valid detail route gets 200 status code."""
    response = testapp.get(Sample_stock)
    assert response.status_code == 200


def test_detail_route_has_correct_entry(testapp):
    """Test that the detail route shows correct stock data."""
    response = testapp.get(Sample_stock)
    assert 'company' in response.html.find('company')


def test_detail_route_has_no_login_option(testapp):
    """Test that the detail route has not login option for unauth user."""
    response = testapp.get(Sample_stock)
    assert not response.html.find('a', 'login')


def test_detail_route_unauth_goes_to_404_page_for_invalid_id(testapp):
    """Test that the detail route redirects to 404 page for invalid id."""
    response = testapp.get("/detail_view", status=404)
    assert 'This is not the route you are looking for.' in str(response.html.find('company'))


def test_portfolio_get_route_unauth_gets_403_status_code(testapp):
    """Test that the create GET route gets 403 status code for unauth user."""
    assert testapp.get("/portfolio_view", status=403)


def test_portfolio_post_route_unauth_gets_403_status_code(testapp):
    """Test that the create POST route gets 403 status code for unauth user."""
    assert testapp.post("/portfolio_view", status=403)


def test_logout_route_unauth_gets_403_status_code(testapp):
    """Test that the logout route gets 403 status code for unauth user."""
    assert testapp.get("/logout", status=403)


def test_login_get_route_unauth_gets_200_status_code(testapp):
    """Test that the login GET route gets 200 status code."""
    response = testapp.get("/login_view")
    assert response.status_code == 200


def test_login_get_route_unauth_has_login_form(testapp):
    """Test that the login GET route gets 200 status code."""
    response = testapp.get("/login_view")
    assert len(response.html.find_all('input')) == 2
    assert 'Username' in str(response.html.find('input'))


def test_login_post_route_unauth_incompelete_data_has_400_error(testapp):
    """Test that POST of incomplete data to login route gets a 400 error."""
    data = {
        'username': 'name'
    }
    assert testapp.post("/login_view", data, status=400)


def test_login_post_route_unauth_wrong_data_has_200_status_code(testapp):
    """Test that POST of wrong data to login route gets a 200 status code."""
    data = {
        'username': 'name',
        'password': 'pass'
    }
    response = testapp.post("/login_view", data)
    assert response.status_code == 200


def test_login_post_route_unauth_wrong_data_has_error_message(testapp):
    """Test that POST of wrong data to login route has an error message."""
    data = {
        'username': 'name',
        'password': 'psas'
    }
    response = testapp.post("/login_view", data)
    assert 'incorrect' in str(response.html.find('div', 'alert'))


def test_login_post_route_unauth_correct_data_has_302_status_code(testapp, username, password):
    """Test that POST of correct data to login route has 302 status code."""
    data = {
        'username': username,
        'password': password
    }
    response = testapp.post("/login_view", data)
    assert response.status_code == 302


def test_logout_route_auth_gets_302_status_code(testapp):
    """Test that the logout route gets 302 status code for auth user."""
    response = testapp.get("/logout")
    assert response.status_code == 302


def test_login_post_route_unauth_correct_data_redirects_to_home(testapp, username, password):
    """Test that POST of correct data to login route redirects to home page."""
    data = {
        'username': username,
        'password': password
    }
    response = testapp.post("/login_view", data)
    home = testapp.app.routes_mapper.get_route('home').path
    assert response.location.endswith(home)


def test_logout_route_auth_redirects_to_home(testapp):
    """Test that the logout route redirects to home page."""
    response = testapp.get("/logout")
    home = testapp.app.routes_mapper.get_route('home').path
    assert response.location.endswith(home)


def test_login_post_route_unauth_correct_data_home_has_logout_tab(testapp, username, password):
    """Test that POST of correct data to login route has home page with logout tab."""
    data = {
        'username': username,
        'password': password
    }
    response = testapp.post("/login_view", data)
    next_page = response.follow()
    assert len(next_page.html.find_all('li', 'nav-item')) == 3
    assert 'Logout' in str(next_page.html.find_all('li', 'nav-item')[2])


def test_logout_route_auth_home_has_login_tab(testapp):
    """Test that the logout route has home page with login."""
    response = testapp.get("/logout")
    next_page = response.follow()
    assert len(next_page.html.find_all('li', 'nav-item')) == 2
    assert 'Login' in str(next_page.html.find_all('li', 'nav-item')[1])


def test_login_post_route_unauth_correct_data_adds_auth_tkt_cookie(testapp, username, password):
    """Test that POST of correct data to login route adds auth_tkt cookie."""
    data = {
        'username': username,
        'password': password
    }
    testapp.post("/login_view", data)
    assert 'auth_tkt' in testapp.cookies


def test_login_get_route_auth_has_302_status_code(testapp):
    """Test that GET to login route has 302 status code."""
    response = testapp.get("/login_view")
    assert response.status_code == 302


def test_login_get_route_auth_keeps_auth_tkt_cookie(testapp):
    """Test that GET to login route adds auth_tkt cookie."""
    assert 'auth_tkt' in testapp.cookies
    testapp.get("/login_view")
    assert 'auth_tkt' in testapp.cookies


def test_login_post_route_auth_has_302_status_code(testapp):
    """Test that POST to login route has 302 status code."""
    response = testapp.post("/login_view")
    assert response.status_code == 302


def test_login_post_route_auth_keeps_auth_tkt_cookie(testapp):
    """Test that POST to login route adds auth_tkt cookie."""
    assert 'auth_tkt' in testapp.cookies
    testapp.post("/login_view")
    assert 'auth_tkt' in testapp.cookies


def test_home_route_auth_gets_200_status_code(testapp):
    """Test that the home route gets 200 status code."""
    response = testapp.get("/")
    assert response.status_code == 200


def test_detail_route_auth_for_valid_id_gets_200_status_code(testapp):
    """Test that the detail route of a valid gets 200 status code."""
    response = testapp.get("/detail_view")
    assert response.status_code == 200


def test_logout_route_auth_removes_auth_tkt_cookie(testapp):
    """Test that the logout route removes the auth_tkt cookie."""
    testapp.get("/logout")
    assert 'auth_tkt' not in testapp.cookies
