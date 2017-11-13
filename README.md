# Stock Analysis 
Utitlizing Python's strong suits to pair with Machine Learning, Stock Analysis will predict the possible life for a given stock.
## Getting Started
- Clone project into local file system. 
    - ```git clone https://github.com/ztaylor2/stock-analysis.git```
- Change directory into your newly created project.
    - ```cd stock_analysis```
- Create a Python virtual environment.
    - ```python3 -m venv ENV```
- Install the project in editable mode with its testing requirements.
    - ```pip install -e .[testing]```
- Configure the database.
    - ```initdb development.ini```
- Run your project's tests.
    - ```pytest```
- Run your project.
    - ```pserve development.ini```
    
## Design & Design Choices
We started off with a basic wire frame of how we desired this application to look.
![Wire Frame](https://github.com/ztaylor2/stock-analysis/blob/jake-template-design/stock_analysis/static/wire_frame.jpg)

From here after keeping discussion with front-end vs. back-end and how we want them to communicate together we refactored a more detailed view and came up with this.
![Detailed Frame](https://github.com/ztaylor2/stock-analysis/blob/jake-template-design/stock_analysis/static/detailed_frame.jpg)
## Influences and Attributions
This project would not be possible without the inspiration from these individuals and the help of some awesome libraries.
### People
* [Siraj Reval](https://twitter.com/sirajraval)
* []()
* []()
* []()

### Libraries
* [Pyramid](https://trypyramid.com/)
* [Bokeh](https://bokeh.pydata.org/en/latest/)
* []()
* []()

## License
Stock Analysis is offered under the [MIT license](https://opensource.org/licenses/MIT) and shown in the LICENSE file.
## Authors
Stock Analysis is possible by the following [contributors](https://github.com/ztaylor2/stock-analysis/graphs/contributors):
* [Zach Taylor](https://github.com/ztaylor2)
* [Kinley Ramson](https://github.com/nothingnessbird)
* [Michael Shinners](https://github.com/mshinners)
* [Chelsea Dole](https://github.com/chelseadole)
* [Jacob Carstens](https://github.com/Loaye)