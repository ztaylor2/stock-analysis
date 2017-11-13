"""Views for the Stock Analysis app."""
from pyramid.view import view_config
from bokeh.plotting import figure, output_file, show
import pandas_datareader.data as web

import datetime


@view_config(route_name='home', renderer='stock_analysis:templates/home.jinja2')
def home_view(request):
    """Home view for stock analysis app."""

    start = datetime.datetime(2015, 1, 1)

    end = datetime.datetime(2015, 12, 31)

    stock_data = web.DataReader("FB", 'yahoo', start, end)

    dates = stock_data.index.values
    prices = stock_data['Close'].values

    # output to static HTML file
    output_file("lines.html")

    # create a new plot with a title and axis labels
    p = figure(title="Stock Analysis", x_axis_label='x', y_axis_label='y')

    # add a line renderer with legend and line thickness
    p.line(dates, prices, legend="Temp.", line_width=2)

    # show the results
    show(p)

    return {}
