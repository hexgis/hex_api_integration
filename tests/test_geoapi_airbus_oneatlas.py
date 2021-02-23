#!/usr/bin/env python

"""Tests for `hex_api_integration` package."""

import os
import pytest
import sys

from hex_api_integration.geoapi_airbus.oneatlas import Api as GeoApi

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
def bbox():
    """
    Bbox fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return [-100.10742, -28.14950, 15.20507, 5.26600]


@pytest.fixture
def preview_url():
    """
    Preview Url fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return "https://access.foundation.api.oneatlas.airbus.com/api/" \
        "v1/items/592f885d-39ee-499b-a447-4311f0b2db00/quicklook"


def test_get_oneatlas_url(geo_api):
    """Tests get oneatlas url private method for GeoAPI"""
    oneatlas_url = geo_api.get_api_url()
    assert oneatlas_url
    assert type(oneatlas_url) == str


def test_get_payload_default_data(geo_api):
    """Tests get payload dict method for GeoAPI with default data"""
    payload = geo_api.get_payload()
    assert payload
    assert type(payload) == dict
    assert payload.get("sortBy") == "-acquisitionDate,cloudCover"


def test_get_payload_data_parameter(geo_api):
    """Tests get payload dict method for GeoAPI with parameter data"""
    payload = geo_api.get_payload(workspace="TEST")
    assert payload
    assert type(payload) == dict
    assert payload.get("cloudCover") == '100['


def test_get_response_data_parameter(geo_api, bbox):
    """Tests get response data method for GeoAPI"""
    payload = geo_api.get_payload(
        bbox=bbox,
        acquisition_date_range=["2020-01-01", "2020-02-01"],
        constellation=["SPOT"],
    )
    assert payload
    assert type(payload) == dict
    assert payload.get("acquisitionDate")
    assert payload.get("cloudCover") == '100['
    response = geo_api.get_response_data(payload)
    assert response
    assert response.status_code == 200
    data = response.json()
    assert data.get("features")
    assert data.get("totalResults")
    assert data.get("itemsPerPage")
    assert data.get("itemsPerPage") == payload["itemsPerPage"]

    features = data.get("features")
    for feature in features:
        assert feature.get("geometry")
        assert feature.get("_links")
        assert feature.get("_links").get("thumbnail")
        assert feature.get("_links").get("thumbnail").get("href")


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


def test_get_response_data_image_path_feature(geo_api, bbox):
    """
    Tests get response image path for GeoAPI with path from feature
    """
    payload = geo_api.get_payload(
        bbox=bbox,
        acquisition_date_range=["2020-01-01", "2020-02-01"],
        constellation=["PHR"],
        cloud_cover=10,
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
    print("\n\n")
    print(thumbs)
    print("\n\n")
    assert response.status_code == 200
