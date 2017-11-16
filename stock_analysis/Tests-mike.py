"""Tests for the Stock Analysis app."""

from __future__ import unicode_literals
from pyramid.httpexceptions import HTTPNotFound, HTTPFound, HTTPBadRequest
from datetime import datetime
import os
import pytest


""" UNIT TESTS FOR MODELS """


def test_(db_session):
    """Test that Portfolio constructed when stock is entered."""
    from stock_analysis.models import Portfolio
    assert len(db_session.query(Portfolio).all()) == 0
    entry = Sample_stock(
        company='Yahoo',
        exchange='NYSE',
        ticker='YHOO',
        current='18.55',
        growth='.50',
        open='18.05',
        high='18.95',
        low='18.05'
    )
    db_session.add(stock)
    assert len(db_session.query(Portfolio).all()) == 1


def test_to_dict_puts_all_properties_in_a_dictionary(test_entry):
    """Test that all properties of a stock are in to_dict dictionary."""
    stock_detail = test_entry.to_dict()
    assert all(prop in stock_detail for prop in ['company', 'exchange', 'ticker', 'current', 'growth', 'open', 'high', 'low'])


def test_to_html_dict_puts_all_properties_in_a_dictionary(test_entry):
    """Test that all properties of a stock are in to_html_dict dictionary."""
    stock_detail = test_entry.to_html_dict()
    assert all(prop in stock_detail for prop in ['company', 'exchange', 'ticker', 'current', 'growth', 'open', 'high', 'low'])


""" UNIT TESTS FOR VIEW FUNCTIONS """
