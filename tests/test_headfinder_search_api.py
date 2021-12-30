#!/usr/bin/env python

"""Tests for `hex_api_integration` package."""

import os
import pytest
import sys

from hex_api_integration.headfinder_api.search_api import Api as SearchApi

if os.getenv('TEST_HEADFINDER_API_KEY') is None:
    sys.exit('Please define env TEST_HEADFINDER_API_KEY for testing')


@pytest.fixture
def search_api():
    """SearchAPI fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return SearchApi(os.getenv('TEST_HEADFINDER_API_KEY'))


@pytest.fixture
def geom():
    """Geometry fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return ('polygon(((53.715,5.037),'
            '(52.018,26.307),'
            '(37.535,16.287),'
            '(43.028,-1.290)))')


@pytest.fixture
def bbox():
    """Geometry fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return [
        -48.277309693614235,
        -16.047997768048294,
        -47.296779908457985,
        -15.51277906427387
    ]


@pytest.fixture
def scene_id():
    """
    Scene ID fixture data.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return 'SV-1-03_PMS_20200907_0_3283473'


def test_get_search_api_url(search_api):
    """Tests get geostore url private method for SearchAPI"""
    search_api_url = search_api.get_search_api_url()
    assert search_api_url
    assert type(search_api_url) == str


def test_get_payload_data_parameter(search_api):
    """Tests get payload dict method for SearchAPI with parameter data"""
    payload = search_api.get_payload(scene_id='TEST')
    assert payload
    assert type(payload) == dict
    assert payload.get('scenename') == 'TEST'


def test_get_response_data_parameter_geom(search_api, geom):
    """Tests get response data method for SearchAPI"""
    payload = search_api.get_payload(
        geometry=geom,
        start_date='2020-07-15',
        end_date='2020-08-01',
        max_scenes=2,
        satellites=['SuperView', 'EarthScanner-KF1'],
    )
    assert payload
    assert type(payload) == dict
    assert payload.get('aoi')
    response = search_api.get_response_data(payload)

    assert response
    assert response.text
    assert len(response.text) > 0
    assert '&jsonscenelist=' in response.text
    data = response.text.split('&jsonscenelist=')[1]
    data = data.split('&hits=')[0]
    assert len(data)
    assert data != '[]'


def test_get_response_data_parameter_bbox(search_api, bbox):
    """Tests get response data method for SearchAPI"""
    payload = search_api.get_payload(
        bbox=bbox,
        start_date='2020-07-15',
        end_date='2020-08-01',
        max_scenes=2,
        satellites=['SuperView', 'EarthScanner-KF1'],
    )
    assert payload
    assert type(payload) == dict
    assert payload.get('aoi')
    response = search_api.get_response_data(payload)

    assert response
    assert response.text
    assert len(response.text) > 0
    assert '&jsonscenelist=' in response.text
    data = response.text.split('&jsonscenelist=')[1]
    data = data.split('&hits=')[0]
    assert len(data)
    assert data != '[]'


def test_get_image_payload(search_api, scene_id):
    """Tests get image payload dict method for SearchAPI with parameter data"""
    payload = search_api.get_image_payload(scene_id)
    assert payload
    assert type(payload) == dict
    assert payload.get('imgformat') == 'png'


def test_get_response_data_image_blob(search_api, scene_id):
    """Tests get response image blob data method for SearchAPI"""
    payload = search_api.get_image_payload(scene_id)
    preview = search_api.get_image_data(payload)
    assert preview
    assert preview.headers['Content-Type'] == 'image/png'
