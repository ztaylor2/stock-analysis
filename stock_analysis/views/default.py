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
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
import requests


@view_config(route_name='home', renderer='stock_analysis:templates/home.jinja2', permission=NO_PERMISSION_REQUIRED)
def home_view(request):
    """Home view for stock analysis app."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        #  ALSO CHECK THAT IT'S A LOGIN POST REQUEST
        username = request.POST['username']
        password = request.POST['password']
        if is_authorized(request, username, password):
            headers = remember(request, username)
            return HTTPFound(request.route_url('portfolio'), headers=headers)
        return {
            'error': 'Username/password combination invalid.'
        }
    if request.method == 'POST':
        #  ALSO CHECK THAT IT'S A REGISTER ACCOUNT POST REQUEST
        new_username = request.POST['username']
        new_password = request.POST['password']
        new_account = User(
            username=new_username,
            password=new_password
        )
        request.dbsession.add(new_account)


@view_config(route_name='detail', renderer='stock_analysis:templates/detail.jinja2')
def detail_view(request):
    """Home view for stock analysis app."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':

        stock = request.POST['stock_ticker'].upper()

        def get_symbol(symbol):
            """Get company name from stock ticker for graph title."""
            url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
            result = requests.get(url).json()
            for x in result['ResultSet']['Result']:
                if x['symbol'] == symbol:
                    return x['name'], x['exchDisp']
        company, exchange = get_symbol(stock)

        start = datetime.datetime(2015, 8, 1)
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

        eighty_percent_of_dates = days_from_beginning[:(len(days_from_beginning) - int(round(len(days_from_beginning) * .2)))]
        eighty_dates_reshape = np.reshape(eighty_percent_of_dates, (len(eighty_percent_of_dates), 1))

        twenty_percent_of_dates = days_from_beginning[(len(days_from_beginning) - int(round(len(days_from_beginning) * .2))):]
        twenty_dates_reshape = np.reshape(eighty_percent_of_dates, (len(eighty_percent_of_dates), 1))


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
        # svr_rbf = SVR(kernel='rbf', C=1e3, gamma=1E-4, degree=5)
        svr_rbf.fit(eighty_dates_reshape, prices[:len(eighty_dates_reshape)])
        svr_rbf_prediction = svr_rbf.predict(dates_reshape)


        mean_p = np.mean([lin_regr_prediction, poly_prediction, svr_rbf_prediction], axis=0)

        # svr_rbf_prediction_test = []

        # for date in dates_reshape:
        #     svr_rbf_prediction_test.append(svr_rbf.predict(date)[0])

        # import pdb; pdb.set_trace()

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
        p.legend.location = "top_left"
        p.title.text_font_size = "1em"

        # save script and div components to put in html
        script, div = components(p)

        return {
            "div": div,
            "script": script,
        }


@view_config(route_name='portfolio', renderer='stock_analysis:templates/portfolio.jinja2')
def portfolio_view(request):
    """Portfolio view for stock analysis app."""
    return {}


@view_config(route_name='logout')
def logout(request):
    """Logout of stock account."""
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)

@view_config(route_name='process_symbol')
def process_symbol(request):
    """Home view for stock analysis app."""
    print('in process')

