"""Views for the Stock Analysis app."""
from __future__ import division
from pyramid.view import view_config
from bokeh.plotting import figure
import pandas_datareader.data as web
from bokeh.embed import components
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from pandas_datareader._utils import RemoteDataError
from alpha_vantage.timeseries import TimeSeries
from stock_analysis.security import is_authorized
import datetime
from stock_analysis.models.mymodel import User, Portfolio
import numpy as np
from sklearn.svm import SVR
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from treeinterpreter import treeinterpreter as ti
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import classification_report,confusion_matrix
import requests


@view_config(route_name='home', renderer='stock_analysis:templates/home.jinja2', permission=NO_PERMISSION_REQUIRED)
def home_view(request):
    """Home view for stock analysis app."""
    return {}


@view_config(route_name='detail', renderer='stock_analysis:templates/detail.jinja2')
def detail_view(request):
    """Detail stock view for stock analysis app."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':

        stock = request.POST['stock_ticker'].upper()

        def _get_symbol(symbol):
            """Get company name from stock ticker for graph title."""
            url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
            result = requests.get(url).json()
            for x in result['ResultSet']['Result']:
                if x['symbol'] == symbol:
                    return x['name'], x['exchDisp']

        try:
            company, exchange = _get_symbol(stock)
        except TypeError:
            return {
                "error": "No data on {}".format(stock)
            }

        start = datetime.datetime(2015, 8, 1)
        end = datetime.datetime(2017, 11, 1)
        try:
            stock_data = web.DataReader(stock, 'yahoo', start, end)
        except RemoteDataError:
            return {
                "error": "Error retrieving {} data, try again.".format(stock)
            }

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

        eighty_percent_of_dates = days_from_beginning[:(len(days_from_beginning) - int(round(len(days_from_beginning) * .2)))]
        eighty_dates_reshape = np.reshape(eighty_percent_of_dates, (len(eighty_percent_of_dates), 1))

        dates_reshape = np.reshape(days_from_beginning, (len(days_from_beginning), 1))

        # Linear Regression
        lin_regr = linear_model.LinearRegression()
        lin_regr.fit(eighty_dates_reshape, prices[:len(eighty_dates_reshape)])
        lin_regr_prediction = lin_regr.predict(dates_reshape)

        # Polynomial Regression
        model = Pipeline([('poly', PolynomialFeatures(degree=3)),
                          ('linear', LinearRegression(fit_intercept=False))])
        model = model.fit(eighty_dates_reshape, prices[:len(eighty_dates_reshape)])
        poly_prediction = model.predict(dates_reshape)

        # Support Vector Machine
        svr_rbf = SVR(kernel='rbf', C=1, gamma=1E-3)
        svr_rbf.fit(eighty_dates_reshape, prices[:len(eighty_dates_reshape)])
        svr_rbf_prediction = svr_rbf.predict(dates_reshape)

        mean_p = np.mean([lin_regr_prediction, poly_prediction, svr_rbf_prediction], axis=0)

        rf = RandomForestRegressor()
        rf.fit(eighty_dates_reshape, prices[:len(eighty_dates_reshape)])
        rf_prediction, bias, contributions = ti.predict(rf, dates_reshape)

        # create a new plot with a title and axis labels
        p = figure(title="{}  -  {}: {}".format(company, exchange, stock), x_axis_label='Date',
                   y_axis_label='Price', width=800, height=350,
                   x_axis_type="datetime", sizing_mode='scale_width')
        p.circle(dates, prices, legend="Historical Data", line_color="black", fill_color="white", size=6)
        p.line(dates, lin_regr_prediction, legend="Linear Regression",
               line_color="orange", line_width=2)
        p.line(dates, poly_prediction, legend="Polynomial Regression",
               line_color="green", line_width=2)
        p.line(dates, svr_rbf_prediction, legend="Support Vector Machine",
               line_color="blue", line_width=2)
        p.line(dates, mean_p, legend="Mean(L, P, SVM)",
               line_color="gray", line_width=2)
        p.line(dates, rf_prediction, legend="Random Forest Regression",
               line_color="black", line_width=2)
        p.legend.location = "top_left"
        p.title.text_font_size = "1em"

        # save script and div components to put in html
        script, div = components(p)

        return {
            "div": div,
            "script": script,
        }

@view_config(route_name='portfolio', renderer='stock_analysis:templates/portfolio.jinja2', permission='secret')
def portfolio_view(request):
    """View for logged in portfolio."""
    if request.method == 'GET':
        username = request.authenticated_userid
        stock_str = request.dbsession.query(Portfolio).get(username)
        if stock_str.stocks != '':
            stock_list = stock_str.stocks.split()
            stock_detail = {}

            def get_symbol(symbol):
                """Get company name from stock ticker for graph title."""
                url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
                result = requests.get(url).json()
                for x in result['ResultSet']['Result']:
                    if x['symbol'] == symbol:
                        return x['name'], x['exchDisp']

            for stock in stock_list:
                company, exchange = get_symbol(stock)
                ts = TimeSeries(key='FVBLNTQMS4063FIN')
                data, meta_data = ts.get_intraday(stock)
                data = data[max(data)]
                open_price = round(float(data['1. open']), 2)
                high = round(float(data['2. high']), 2)
                low = round(float(data['3. low']), 2)
                current = round(float(data['4. close']), 2)
                volume = data['5. volume'], 2
                growth = (float(data['4. close']) - float(data['1. open'])) / float(data['1. open'])
                if growth > 0:
                    growth = '+' + "{:.2%}".format(growth)
                else:
                    growth = "{:.1%}".format(growth)
                stock_detail[stock] = {'growth': growth, 'company': company, 'volume': volume, 'open': open_price, 'high': high, 'low': low, 'ticker': stock, 'current': current}
            return {'stock_detail': stock_detail}
        return {}

    if request.method == 'POST':
        username = request.authenticated_userid
        new_ticker = request.POST['new_ticker']
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(new_ticker)
        response = requests.get(url).json()
        if response['ResultSet']['Result'] == []:
            return {"error": "Stock ticker invalid"}
        port_stocks = request.dbsession.query(Portfolio).get(username)
        # if new_ticker.upper() in port_stocks.split():
        #     return {"error": "Stock ticker already in your portfolio"}
        # else:
        portfolio_stocks = request.dbsession.query(Portfolio).get(username)
        if portfolio_stocks.stocks:
            portfolio_stocks.stocks += (' ' + new_ticker)
        else:
            portfolio_stocks.stocks = new_ticker
        request.dbsession.flush()
        return HTTPFound(request.route_url('portfolio'))
    return {}


@view_config(route_name='logout')
def logout(request):
    """Logout of stock account."""
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


@view_config(route_name='process_symbol')
def process_symbol(request):
    """Processing and loading symbol."""
    print('in process')


@view_config(route_name='login', renderer='stock_analysis:templates/login.jinja2', permission=NO_PERMISSION_REQUIRED)
def login_view(request):
    """Login view for stock analysis app."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if is_authorized(request, username, password):
            headers = remember(request, username)
            return HTTPFound(request.route_url('portfolio'), headers=headers)
        return {
            'error': 'Username/password combination invalid.'
        }



@view_config(route_name='register', renderer='stock_analysis:templates/register.jinja2')
def register_view(request):
    """Register view for stock analysis app."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # if username in request.dbsession(User).all():
        #     return {"error": "This username/password combo already exists. Choose another option"}

        new_account = User(
            username=username,
            password=password
        )
        new_portfolio = Portfolio(
            username=username,
            stocks=''
        )
        request.dbsession.add(new_portfolio)
        request.dbsession.add(new_account)
        headers = remember(request, username)
        return HTTPFound(request.route_url('portfolio'), headers=headers)
    return {}


# @view_config(route_name='delete_stock', permission='secret')
# def delete_stock(request):
#     """Delete stock from portfolio."""
#     username = request.authenticated_userid
#     portfolio_stocks = request.dbsession.query(Portfolio).get(username)
#     import pdb; pdb.set_trace()
#     target = request.POST['name']
#     # portfolio_stocks.stocks = [ tick for tick in portfolio_stocks.stocks.split() if tick is not target]
#     username = request.authenticated_userid
#     new_ticker = request.POST['new_ticker']
#     portfolio_stocks = request.dbsession.query(Portfolio).get(username)
#     if portfolio_stocks.stocks:
#         portfolio_stocks.stocks += (' ' + new_ticker)
#     else:
#         portfolio_stocks.stocks = new_ticker
#     request.dbsession.flush()
#     return HTTPFound(request.route_url('portfolio'))
