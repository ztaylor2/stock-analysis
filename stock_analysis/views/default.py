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
    if request.method == 'GET':
        return {}
    if request.method == 'POST':

        stock = request.POST['stock_ticker'].upper()

        start = datetime.datetime(2016, 11, 1)
        end = datetime.datetime(2017, 11, 1)
        stock_data = web.DataReader(stock, 'yahoo', start, end)
        list_of_dates = []
        dates = stock_data.index.values.tolist()
        for x in dates:
            list_of_dates.append(x)
        prices = stock_data['Close'].values.tolist()



        dates = np.reshape(dates, (len(dates), 1))
        svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
        svr_rbf.fit(dates, prices)
        # import pdb; pdb.set_trace()
        svr_prediction = svr_rbf.predict(dates).tolist()

        # create a new plot with a title and axis labels
        p = figure(title="Stock Analysis", x_axis_label='Time', y_axis_label='Price')

        p.multi_line([list_of_dates, list_of_dates], [prices, svr_prediction],
                     color=["firebrick", "navy"], legend="Temp.", alpha=[0.8, 0.3], line_width=2)

        # save script and div components to put in html
        script, div = components(p)

        return {
            "div": div,
            "script": script,
        }
    return {}
