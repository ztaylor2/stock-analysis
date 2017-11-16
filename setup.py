"""Setup file for stock analysis application."""
from setuptools import setup, find_packages

requires = [
    'plaster_pastedeploy',
    'pyramid >= 1.9a',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_retry',
    'pyramid_tm',
    'ipython',
    'pyramid_ipython',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'pandas',
    'numpy',
    'passlib',
    'scikit-learn',
    'matplotlib',
    'bokeh',
    'scipy',
    'pandas-datareader',
    'psycopg2',
    'alpha_vantage',
    'pytest',
    'webtest',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest-cov',
    'tox',
]

setup(
    name='Stock Analysis',
    version='0.0',
    description='Stock analysis application written in python',
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = stock_analysis:main',
        ],
        'console_scripts': [
            'initdb = stock_analysis.scripts.initializedb:main',
        ],
    },
)
