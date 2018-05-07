# Stock Analysis

Zephyr Stock Analysis is a python web application that allows the user to track a portfolio of stocks and perform data analysis on any given stock ticker. The analytical and machine learning regressions train on the first 80% of the data and then attempt to predict the last 20%. 

## Getting Started
* Clone project into local file system. 
    * ```git clone https://github.com/ztaylor2/stock-analysis.git```
* Change directory into your newly created project.
    * ```cd stock_analysis```
* Create a Python virtual environment.
    * ```python3 -m venv ENV```
* Install the project in editable mode with its testing requirements.
    * ```pip install -e .[testing]```
* Configure the database.
    * ```initdb development.ini```
* Run your project's tests.
    * ```pytest```
* Run your project.
    * ```pserve development.ini```
    
## Design & Design Choices
We started off with a basic wire frame of how we desired this application to look.
![Wire Frame](https://github.com/ztaylor2/stock-analysis/blob/jake-template-design/stock_analysis/static/wire_frames/wire_frame.jpg)

From here after keeping discussion with front-end vs. back-end and how we want them to communicate together we refactored a more detailed view and came up with this:
![Detailed Frame](https://github.com/ztaylor2/stock-analysis/blob/jake-template-design/stock_analysis/static/wire_frames/detailed_frame.jpg)

We finally have something we are happy with. How we want to mock this up is the next obstacle to tackle. We decided to template with Pyramid and Jinja, then to design the application we went with SCSS.

Coming to a road block with rendering graphs and for User Experience/User Interface(UX/UI), we decided to condense two of our view into one. We got this :
![Refactored Detail Frame](https://github.com/ztaylor2/stock-analysis/blob/jake-template-design/stock_analysis/static/wire_frames/refactored_detail_frame.jpg)
## Influences and Attributions
This project would not be possible without the inspiration from these individuals and the help of some awesome libraries.
### People
-----------
* Siraj Reval [Twitter](https://twitter.com/sirajraval) [GitHub](https://github.com/llSourcell)
### Libraries
--------------
#### Machine Learning
* [SciKit](http://scikit-learn.org/stable/)
#### Data Management
* [Pandas](https://pandas-datareader.readthedocs.io/en/latest/remote_data.html#yahoo-finance)
* [BeatifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [Tree Interpreter](https://github.com/andosa/treeinterpreter)
* [NumPy](http://www.numpy.org/)
#### Templating
* [Pyramid](https://trypyramid.com/)
* [Jinja](http://jinja.pocoo.org/)

#### API
* [Yahoo Finance API](https://www.npmjs.com/package/yahoo-finance)
#### Design
* [Bokeh](https://bokeh.pydata.org/en/latest/)
    * ```Graph and Charting```
* [SCSS](http://sass-lang.com/)
    * ```Functional Designing```
* [Icomoon](https://icomoon.io/)
    * ```SVG and Icons```
* [BootStrap](https://getbootstrap.com/)
    * ```Front-End Development```
## License
Stock Analysis is offered under the [MIT license](https://opensource.org/licenses/MIT) and shown in the LICENSE file.
## Authors
Stock Analysis is possible by the following [contributors](https://github.com/ztaylor2/stock-analysis/graphs/contributors):
* [Zach Taylor](https://github.com/ztaylor2)
* [Michael Shinners](https://github.com/mshinners)
* [Chelsea Dole](https://github.com/chelseadole)
* [Jacob Carstens](https://github.com/Loaye)
