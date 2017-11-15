"""Views for the Stock Analysis app."""
from pyramid.view import view_config
from bokeh.plotting import figure
import pandas_datareader.data as web
from bokeh.embed import components
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from stock_analysis.security import is_authorized
import datetime
from stock_analysis.models.mymodel import User
import pandas as pd
import numpy as np
from sklearn.svm import SVR
from sklearn import linear_model
import os
import pdb 


stock_dict = {'Book_Value_per_Share': '10.051',
              'name': 'Yahoo',
              'symbol': 'YHOO',
              'price': '14.96',
              'growth': '2.48',
              'percent': '1.47%'}


@view_config(route_name='home', renderer='stock_analysis:templates/home.jinja2', permission=NO_PERMISSION_REQUIRED)
def home_view(request):
    """Home view for stock analysis app."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if 'login' in request.POST:
            if is_authorized(request, username, password):
                headers = remember(request, username)
                return HTTPFound(request.route_url('portfolio'), headers=headers)
            return {
                'error': 'Username/password combination invalid.'
            }
        elif 'register' in request.POST:
            new_account = User(
                username=username,
                password=password
            )
            request.dbsession.add(new_account)
            headers = remember(request, username)
            return HTTPFound(request.route_url('portfolio'), headers=headers)
        return {}


@view_config(route_name='detail', renderer='stock_analysis:templates/detail.jinja2')
def detail_view(request):
    """Home view for stock analysis app."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':

        stock = request.POST['stock_ticker'].upper()

        start = datetime.datetime(2016, 11, 1)
        end = datetime.datetime(2017, 11, 1)
        stock_data = web.DataReader(stock, 'yahoo', start, end)
        dates = stock_data.index.values
        prices = stock_data['Close'].values

        # convert numpy dates into python datetime objects
        dates_python = []
        for date in dates:
            dates_python.append(datetime.datetime.utcfromtimestamp(date.tolist()/1e9))

        # convert dates to list of days ago
        last = dates_python[-1]
        first = dates_python[0]
        total_diff = last - first
        days_from_beginning = []
        for date in dates_python:
            diff = last - date
            days_from_beginning.append(total_diff.days - diff.days)

        # eight_percet_of_dates = dates[:(len(dates) - int(round(len(dates) * .2)))]
        # eighty_dates_reshape = np.reshape(eight_percet_of_dates, (len(eight_percet_of_dates), 1))

        dates_reshape = np.reshape(days_from_beginning, (len(days_from_beginning), 1))

        # Linear Regression
        lin_regr = linear_model.LinearRegression()
        lin_regr.fit(dates_reshape, prices)
        lin_regr_prediction = lin_regr.predict(dates_reshape)


        # Support Vector Machine
        svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
        svr_rbf.fit(dates_reshape, prices)
        svr_rbf_prediction = svr_rbf.predict(dates_reshape)


        # create a new plot with a title and axis labels
        p = figure(title="Stock Analysis", x_axis_label='Time', y_axis_label='Price')
        p.multi_line([dates, dates, dates], [prices, lin_regr_prediction, svr_rbf_prediction],
                     color=["firebrick", "navy"], legend="Temp.", alpha=[0.8, 0.3], line_width=2)


        # save script and div components to put in html
        script, div = components(p)

        return {
            "div": div,
            "script": script,
        }


@view_config(route_name='portfolio', renderer='stock_analysis:templates/portfolio.jinja2')
def portfolio_view(request):
    """Portfolio view for stock analysis app."""
    # from alpha_vantage.timeseries import TimeSeries
    # ts = TimeSeries(key=(os.environ.get('AV_API_KEY')))
    # Get json object with the intraday data and another with the call's metadata
    # data, meta_data = ts.get_intraday('GOOGL')
    return stock_dict


@view_config(route_name='logout')
def logout(request):
    """Logout of stock account."""
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


@view_config(route_name='process_symbol')
def process_symbol(request):
    """Home view for stock analysis app."""
    print('in process')
