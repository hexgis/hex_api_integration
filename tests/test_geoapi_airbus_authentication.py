#!/usr/bin/env python

"""Tests for `hex_api_integration` package."""

import os
import pytest
import sys

from hex_api_integration.geoapi_airbus.auth import Authentication

if os.getenv('TEST_AIRBUS_API_KEY') is None:
    sys.exit("Please define env TEST_AIRBUS_API_KEY for testing")


@pytest.fixture
def auth():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    return Authentication(os.getenv("TEST_AIRBUS_API_KEY"))


def test_content(auth):
    """Tests authentication token and errors"""
    assert auth.get_token()
    assert auth.token
    assert not auth.errors


def test_authentication_error(auth):
    """Tests authentication errors"""
    auth = Authentication('test_error')
    assert not auth.errors
    assert not auth.get_token()
    assert auth.errors
    assert not auth.token


def test_api_token_test(auth):
    """Tests authentication test_api_token method"""
    assert auth.test_api_token()


def test_api_get_roles(auth):
    """Tests authentication api_get_roles method"""
    assert auth.get_roles()
    new_auth = Authentication(os.getenv("TEST_AIRBUS_API_KEY"))
    assert new_auth.get_roles()
    assert new_auth.token
    assert not new_auth.errors


def test_api_get_me(auth):
    """Tests authentication api_get_me method"""
    assert auth.get_me()
    new_auth = Authentication(os.getenv("TEST_AIRBUS_API_KEY"))
    assert new_auth.get_me()
    assert new_auth.token
    assert not new_auth.errors


def test_api_get_contract_id(auth):
    """Tests authentication api_get_contract_id method"""
    assert auth.get_contract_id()
    new_auth = Authentication(os.getenv("TEST_AIRBUS_API_KEY"))
    assert new_auth.get_contract_id()
    assert new_auth.token
    assert not new_auth.errors


def test_api_get_all_subscriptions(auth):
    """Tests authentication api_get_all_subscriptions method"""
    assert auth.get_all_subscriptions()
    new_auth = Authentication(os.getenv("TEST_AIRBUS_API_KEY"))
    assert new_auth.get_all_subscriptions()
    assert new_auth.token
    assert not new_auth.errors


def test_api_get_usage(auth):
    """Tests authentication api_get_usage method"""
    assert auth.get_usage()
    new_auth = Authentication(os.getenv("TEST_AIRBUS_API_KEY"))
    assert new_auth.get_usage()
    assert new_auth.token
    assert not new_auth.errors
