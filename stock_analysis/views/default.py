"""Views for the Stock Analysis app."""
from pyramid.view import view_config
from bokeh.plotting import figure
import pandas_datareader.data as web
from bokeh.embed import components
import datetime

import pandas as pd
import numpy as np
from sklearn.svm import SVR


@view_config(route_name='home', renderer='stock_analysis:templates/home.jinja2')
def home_view(request):
    """Home view for stock analysis app."""
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

        # dates_datetime = []

        # i = 0
        # for date in dates:
        #     dates_datetime.append(i)
        #     i += 1

        prices = stock_data['Close'].values

        # eight_percet_of_dates = dates[:(len(dates) - int(round(len(dates) * .2)))]

        # eighty_dates_reshape = np.reshape(eight_percet_of_dates, (len(eight_percet_of_dates), 1))
        dates_reshape = np.reshape(dates, (len(dates), 1))
        # svr_poly = SVR(kernel='poly', C=1e3, degree=2)
        # svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
        # import pdb; pdb.set_trace()


        # svr_poly.fit(dates_reshape, prices)
        # svr_rbf.fit(dates_reshape, prices)

        # works without using 80% of dates

        dates_reshape = np.reshape(dates, (len(dates), 1))
        svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
        svr_rbf.fit(dates_reshape, prices)

        # svr_poly_prediction = svr_poly.predict(dates_reshape)
        svr_rbf_prediction = svr_rbf.predict(dates_reshape)


        # create a new plot with a title and axis labels
        p = figure(title="Stock Analysis", x_axis_label='Time', y_axis_label='Price')

        p.multi_line([dates, dates], [prices, svr_rbf_prediction],
                     color=["firebrick", "navy"], legend="Temp.", alpha=[0.8, 0.3], line_width=2)

        # save script and div components to put in html
        script, div = components(p)

        return {
            "div": div,
            "script": script,
        }


@view_config(route_name='profile', renderer='stock_analysis:templates/profile.jinja2')
def profile_view(request):
    """Home view for stock analysis app."""
    return {}


@view_config(route_name='process_symbol')
def process_symbol(request):
    """Home view for stock analysis app."""
    print('in process')
