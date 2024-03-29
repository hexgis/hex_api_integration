#!/usr/bin/env python

"""Tests for `hex_api_integration` package."""

import os
import pytest
import sys

from hex_api_integration.geoapi_airbus.api import AbstractApi as GeoApi

if os.getenv('TEST_AIRBUS_API_KEY') is None:
    sys.exit("Please define env TEST_AIRBUS_API_KEY for testing")


@pytest.fixture
def geo_api():
    """
    GeoAPI fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return GeoApi(os.getenv("TEST_AIRBUS_API_KEY"))


def test_get_headers(geo_api):
    """Tests get headers private method for GeoAPI"""
    headers = geo_api._get_authenticated_headers()
    assert headers
    assert headers.get("Authorization")


def test_get_included_values(geo_api):
    """Tests get dates private method for GeoAPI"""
    dates = "2018-01-01", "2018-02-01"
    dates = geo_api._get_included_values(dates)
    assert dates
    assert type(dates) == str
    assert dates == "[2018-01-01,2018-02-01["


def test_get_coverage(geo_api):
    """Tests get coverage str private method for GeoAPI"""
    coverage = geo_api._get_less_than_or_equals(10)
    assert coverage
    assert type(coverage) == str
    assert coverage == "10["
