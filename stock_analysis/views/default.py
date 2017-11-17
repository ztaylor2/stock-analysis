"""Views for the Stock Analysis app."""
from __future__ import division
from pyramid.view import view_config
from bokeh.plotting import figure
import pandas_datareader.data as web
from bokeh.embed import components
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from pandas_datareader._utils import RemoteDataError
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
from sklearn.ensemble import RandomForestRegressor
import requests
from bs4 import BeautifulSoup as Soup
from passlib.apps import custom_app_context as context


@view_config(route_name='home', renderer='stock_analysis:templates/home.jinja2', permission=NO_PERMISSION_REQUIRED)
def home_view(request):
    """Home view for stock analysis app."""
    return {}


@view_config(route_name='detail', renderer='stock_analysis:templates/detail.jinja2')
def detail_view(request):  # pragma: no cover
    """Detail stock view for stock analysis app."""
    if request.method == 'GET':
        if 'ticker' in request.GET:
            return {
                'filled_ticker': request.GET['ticker']
            }
        return {}
    if request.method == 'POST':
        stock = request.POST['stock_ticker'].upper()
        start = datetime.datetime.strptime(request.POST['start_date'], "%Y-%m-%d")
        end = datetime.datetime.strptime(request.POST['end_date'], "%Y-%m-%d")

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
            if "ticker" in request.GET:
                return {
                    "error": "Error retrieving {}'s data, try again.".format(stock),
                    "filled_ticker": request.GET['ticker']
                }
            return {
                "error": "No data on {}".format(stock)
            }

        try:
            stock_data = web.DataReader(stock, 'yahoo', start, end)
        except RemoteDataError:
            if "ticker" in request.GET:
                return {
                    "error": "Error retrieving {}'s data, try again.".format(stock),
                    "filled_ticker": request.GET['ticker']
                }
            return {
                "error": "Error retrieving {}'s data, try again.".format(stock)
            }

        dates = stock_data.index.values
        price_open = stock_data['Open'].values
        price_close = stock_data['Close'].values
        price_high = stock_data['High'].values
        price_low = stock_data['Low'].values

        # convert numpy dates into python datetime objects
        dates_python = []
        for date in dates:
            dates_python.append(datetime.datetime.utcfromtimestamp(date.tolist() / 1e9))

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
        lin_regr.fit(eighty_dates_reshape, price_close[:len(eighty_dates_reshape)])
        lin_regr_prediction = lin_regr.predict(dates_reshape)

        # Polynomial Regression
        model = Pipeline([('poly', PolynomialFeatures(degree=3)),
                          ('linear', LinearRegression(fit_intercept=False))])
        model = model.fit(eighty_dates_reshape, price_close[:len(eighty_dates_reshape)])
        poly_prediction = model.predict(dates_reshape)

        # Support Vector Machine
        svr_rbf = SVR(kernel='rbf', C=1, gamma=1E-3)
        svr_rbf.fit(eighty_dates_reshape, price_close[:len(eighty_dates_reshape)])
        svr_rbf_prediction = svr_rbf.predict(dates_reshape)

        mean_p = np.mean([lin_regr_prediction, poly_prediction, svr_rbf_prediction], axis=0)

        rf = RandomForestRegressor()
        rf.fit(eighty_dates_reshape, price_close[:len(eighty_dates_reshape)])
        rf_prediction, bias, contributions = ti.predict(rf, dates_reshape)

        # create a new plot with a title and axis labels
        price_date_plot = figure(title="{}  -  {}: {}".format(company, exchange, stock), x_axis_label='Date',
                                 y_axis_label='Price', width=800, height=800,
                                 x_axis_type="datetime", sizing_mode='stretch_both')
        price_date_plot.circle(dates, price_close, legend="Historical Data", line_color="black", fill_color="white", size=6)
        price_date_plot.line(dates, lin_regr_prediction, legend="Linear Regression",
                             line_color="orange", line_width=2)
        price_date_plot.line(dates, poly_prediction, legend="Polynomial Regression",
                             line_color="green", line_width=2)
        price_date_plot.line(dates, svr_rbf_prediction, legend="Support Vector Machine",
                             line_color="blue", line_width=2)
        price_date_plot.line(dates, mean_p, legend="Mean(L, P, SVM)",
                             line_color="gray", line_width=2)
        price_date_plot.line(dates, rf_prediction, legend="Random Forest Regression",
                             line_color="black", line_width=2)
        price_date_plot.legend.location = "top_left"
        price_date_plot.title.text_font_size = "1em"

        # save script and div components to put in html
        script, div = components(price_date_plot)

        # candle stick plot
        inc = price_close > price_open
        dec = price_open > price_close
        w = 12 * 60 * 60 * 1000 # half day in ms

        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

        candle = figure(x_axis_type="datetime", x_axis_label='Date', tools=TOOLS,
                        width=800, height=800, sizing_mode='stretch_both',
                        y_axis_label='Price',
                        title="{} - Intraday Price Change".format(stock))

        candle.segment(dates, price_high, dates, price_low, color="black")
        candle.vbar(dates[inc], w, price_open[inc], price_close[inc],
                    fill_color="#D5E1DD", line_color="black")
        candle.vbar(dates[dec], w, price_open[dec], price_close[dec],
                    fill_color="#F2583E", line_color="black")
        candle.title.text_font_size = "1em"
        script1, div1 = components(candle)

        # return since beginning of time period
        price_close_list = price_close.tolist()
        stock_change = []
        for x in range(len(price_close_list)):
            stock_change.append(price_close_list[x] / price_close_list[0])

        # create a new plot with a title and axis labels
        returns_beginning = figure(title="{}  -  Return".format(stock),
                                   x_axis_label='Date', y_axis_label='Return',
                                   width=800, height=800, x_axis_type="datetime",
                                   sizing_mode='stretch_both')
        returns_beginning.line(dates[1:], stock_change[1:],
                               line_color="orange", line_width=2)
        script2, div2 = components(returns_beginning)

        # percent change day to day plot
        stock_change = []
        for x in range(len(price_close_list)):
            stock_change.append(np.log(price_close_list[x]) - np.log(price_close_list[x - 1]))

        # create a new plot with a title and axis labels
        percent_change_day = figure(title="{}  -  Day to Day Percentage Change".format(stock),
                                    x_axis_label='Date', y_axis_label='Percent Change',
                                    width=800, height=800, x_axis_type="datetime",
                                    sizing_mode='stretch_both')
        percent_change_day.line(dates[1:], stock_change[1:],
                                line_color="orange", line_width=2)
        script3, div3 = components(percent_change_day)

        analyzed_dict = {
            "div": div,
            "script": script,
            "div1": div1,
            "script1": script1,
            "div2": div2,
            "script2": script2,
            "div3": div3,
            "script3": script3,
            "start": request.POST['start_date'],
            "end": request.POST['end_date'],
            "filled_ticker": request.POST['stock_ticker'].upper(),
        }

        if "ticker" in request.GET and request.GET['ticker'] == request.POST['stock_ticker'].upper():
            # import pdb; pdb.set_trace()
            analyzed_dict['filled_ticker'] = request.GET['ticker']
        return analyzed_dict


@view_config(route_name='portfolio', renderer='stock_analysis:templates/portfolio.jinja2', permission='secret')
def portfolio_view(request):
    """View for logged in portfolio."""
    if request.method == 'GET':
        username = request.authenticated_userid
        stock_str = request.dbsession.query(Portfolio).get(username)
        if stock_str.stocks != '':
            stock_list = stock_str.stocks.split()
            stock_detail = {}
            for tick in stock_list:
                try:
                    stock_detail[tick] = scrape_stock_data(tick)
                except AttributeError:  # pragma: no cover
                    return {
                        "stock_detail": stock_detail,
                        "error": "Stock ticker invalid"
                    }
            return {'stock_detail': stock_detail}
        return {}

    if request.method == 'POST':  # pragma: no cover
        username = request.authenticated_userid
        portfolio_stocks = request.dbsession.query(Portfolio).get(username)
        if "Delete" in request.POST:
            to_delete = request.POST.keys()
            to_delete = to_delete.__next__()
            temp_stock = portfolio_stocks.stocks.split()
            temp_stock.remove(to_delete)
            portfolio_stocks.stocks = ' '.join(temp_stock)
            request.dbsession.flush()
            return HTTPFound(request.route_url('portfolio'))
        new_ticker = request.POST['new_ticker'].upper()
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(new_ticker)
        response = requests.get(url).json()
        if response['ResultSet']['Result'] == []:
            return HTTPFound(request.route_url('portfolio'))
        if portfolio_stocks.stocks:
            if new_ticker not in portfolio_stocks.stocks.split():
                portfolio_stocks.stocks += (' ' + new_ticker)
            else:
                stock_list = portfolio_stocks.stocks.split()
                stock_detail = {}
                for tick in stock_list:
                    stock_detail[tick] = scrape_stock_data(tick)
                return {
                    "stock_detail": stock_detail,
                    "error": "This stock is already in your portfolio"
                }
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


@view_config(route_name='login', renderer='stock_analysis:templates/login.jinja2', permission=NO_PERMISSION_REQUIRED)
def login_view(request):
    """Login view for stock analysis app."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            if is_authorized(request, username, password):
                headers = remember(request, username)
                return HTTPFound(request.route_url('portfolio'), headers=headers)
            return {
                'error': 'Username/password combination invalid.'
            }
        except AttributeError:  # pragma: no cover
            return {"error": "Username/password combination invalid."}


@view_config(route_name='register', renderer='stock_analysis:templates/register.jinja2')
def register_view(request):  # pragma: no cover
    """Register view for stock analysis app."""
    if request.method == 'GET':
        return {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        all_users = request.dbsession.query(User).all()
        for i in range(len(all_users)):
            if all_users[i].username == username:
                return {"error": "This username/password combo already exists"}

        new_account = User(
            username=username,
            password=context.hash(password)
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


def get_symbol(symbol):
    """Get company name from stock ticker for graph title."""
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
    result = requests.get(url).json()
    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name'], x['exchDisp']


def scrape_stock_data(symbol):
    """Scrape stock data from google."""
    company, exchange = get_symbol(symbol)
    r = requests.get('https://finance.google.com/finance?q={}:{}'.format(exchange, symbol))
    parsed = Soup(r.text, 'html.parser')
    price = parsed.find('div', {'id': 'price-panel'}).find_all('span')[1].text
    dollar_change = parsed.find('div', {'id': 'price-panel'}).find_all('span')[3].text
    pct_change = parsed.find('div', {'id': 'price-panel'}).find_all('span')[4].text
    open_price = parsed.find('table', {'class': 'snap-data'}).find_all('td')[5].text
    pe = parsed.find('table', {'class': 'snap-data'}).find_all('td')[11].text
    return {'company': company, 'ticker': symbol, 'price': price, 'dollar_change': dollar_change, 'pct_change': pct_change, 'open_price': open_price, 'pe': pe}
