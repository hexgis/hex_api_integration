#!/usr/bin/env python

"""Tests for `hex_api_integration` package."""

import os
import pytest
import sys

from hex_api_integration.geoapi_airbus.geostore import Api as GeoApi

if os.getenv('TEST_API_KEY') is None:
    sys.exit("Please define env TEST_API_KEY for testing")


@pytest.fixture
def geo_api():
    """
    GeoAPI fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return GeoApi(os.getenv("TEST_API_KEY"))


@pytest.fixture
def geom():
    """
    Geometry fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return "POLYGON ((" \
        " -170.859375 -78.49055166160312," \
        " 191.25 -78.49055166160312," \
        " 191.25 84.86578186731522," \
        " -170.859375 84.86578186731522," \
        " -170.859375 -78.49055166160312))"


@pytest.fixture
def preview_url():
    """
    Preview Url fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return "https://search.federated.geoapi-airbusds.com/" \
        "api/v1/productTypes/SPOTArchive1.5Mono/products/" \
        "DS_SPOT7_201801070929101_CB1_CB1_CB1_CB1_W021S78_01627" \
        "?size=LARGE"


def test_get_headers(geo_api):
    """Tests get headers private method for GeoAPI"""
    headers = geo_api._Api__get_authenticated_headers()
    assert headers
    assert headers.get("Authorization")


def test_get_dates(geo_api):
    """Tests get dates private method for GeoAPI"""
    dates = "2018-01-01", "2018-02-01"
    dates = geo_api._Api__get_dates(dates)
    assert dates
    assert type(dates) == str
    assert dates == "[2018-01-01,2018-02-01["


def test_get_sort_keys(geo_api):
    """Tests get sort keys private method for GeoAPI"""
    sort_keys = geo_api._Api__get_sort_keys()
    assert sort_keys
    assert type(sort_keys) == str


def test_get_coverage(geo_api):
    """Tests get coverage str private method for GeoAPI"""
    coverage = geo_api._Api__get_less_than_or_equals(10)
    assert coverage
    assert type(coverage) == str
    assert coverage == "10["


def test_get_geostore_url(geo_api):
    """Tests get geostore url private method for GeoAPI"""
    geostore_url = geo_api.get_geostore_url()
    assert geostore_url
    assert type(geostore_url) == str


def test_get_payload_default_data(geo_api):
    """Tests get payload dict method for GeoAPI with default data"""
    payload = geo_api.get_payload()
    assert payload
    assert type(payload) == dict
    assert payload.get("sortKeys") == "sortKeys=acquisitionDate,,0"


def test_get_payload_data_parameter(geo_api):
    """Tests get payload dict method for GeoAPI with parameter data"""
    payload = geo_api.get_payload(sensorType="TEST")
    assert payload
    assert type(payload) == dict
    assert payload.get("sensorType") == "TEST"


def test_get_response_data_parameter(geo_api, geom):
    """Tests get response data method for GeoAPI"""
    payload = geo_api.get_payload(
        geometry=geom,
        acquisitionDates=["2020-01-01", "2020-02-01"],
        constellation=["SPOT"],
        cloudCover=10,
    )
    assert payload
    assert type(payload) == dict
    assert payload.get("acquisitionDate")
    response = geo_api.get_response_data(payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("totalResults")
    assert data.get("startIndex")
    assert data.get("itemsPerPage")
    assert data.get("features")
    assert data.get("itemsPerPage") == payload["count"]

    features = data.get("features")
    for feature in features:
        assert feature.get("geometry")
        assert feature.get("quicklooks")
        thumbnails = filter(
            lambda x: x.get("size") == "LARGE",
            feature.get("quicklooks")
        )
        thumbnails = next(thumbnails).get('image')
        assert thumbnails


def test_get_response_data_image_blob(geo_api, preview_url):
    """Tests get response image blob data method for GeoAPI"""
    thumbs = geo_api.get_image_data(preview_url)
    assert thumbs

    thumbs = geo_api.get_image_data(preview_url + "err")
    assert not thumbs


def test_get_response_data_image_path(geo_api, preview_url):
    """Tests get response image path method for GeoAPI"""
    thumbs = geo_api.get_image_path(
        preview_url=preview_url
    )
    assert os.path.exists(thumbs)

    thumbs = geo_api.get_image_path(
        preview_url=preview_url + "test"
    )
    assert not thumbs


def test_get_response_data_image_path_error(geo_api, preview_url):
    """Tests get response image path for GeoAPI with ValueError"""
    with pytest.raises(ValueError):
        geo_api.get_image_path(
            feature=True,
            preview_url=preview_url
        )


def test_get_response_data_image_path_feature(geo_api, geom):
    """
    Tests get response image path for GeoAPI with path from feature
    """
    payload = geo_api.get_payload(
        geometry=geom,
        acquisitionDates=["2020-01-01", "2020-02-01"],
        constellation=["PLEIADES"],
        cloudCover=10,
    )
    assert payload
    assert type(payload) == dict
    assert payload.get("acquisitionDate")

    response = geo_api.get_response_data(payload)
    data = response.json()
    thumbs = geo_api.get_image_path(
        feature=data.get("features")[0]
    )
    assert data
    assert thumbs
    assert response.status_code == 200
