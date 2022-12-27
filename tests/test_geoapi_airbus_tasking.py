#!/usr/bin/env python

"""Tests for `hex_api_integration` package."""

import os
import pytest
import sys

from hex_api_integration.geoapi_airbus.tasking import Api as GeoApi

if os.getenv('TEST_AIRBUS_API_KEY') is None:
    sys.exit('Please set env TEST_AIRBUS_API_KEY for testing')


@pytest.fixture
def geo_api():
    """GeoAPI fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return GeoApi(os.getenv('TEST_AIRBUS_API_KEY'))


def test_get_headers(geo_api):
    """Tests get headers private method for GeoAPI."""

    headers = geo_api._get_authenticated_headers()
    assert headers
    assert headers.get('Authorization')


def test_get_cis_contracts_ids(geo_api):
    """Tests get cis contract ids method for GeoAPI."""

    cis_contract_ids = geo_api.get_cis_contract_ids()
    assert cis_contract_ids
    assert len(cis_contract_ids) > 0


def test_get_taskings(geo_api):
    """Tests get taskings method for GeoAPI."""

    taskings = geo_api.get_taskings_from_contract_ids()
    assert taskings
    # TO-DO: implements taskings validation.
