import os
import sys

from django.test import TestCase
from geoapi_airbus.auth import Authentication
from geoapi_airbus.geostore import Api as GeoApi

if os.getenv('TEST_API_KEY') is None:
    sys.exit("Please define env TEST_API_KEY for testing")


class TestAuthentication(TestCase):

    def setUp(self):
        self.api_key = os.getenv("TEST_API_KEY")
        self.auth = Authentication(self.api_key)

    def test_authentication_assertion(self):
        """Tests authentication token and errors"""
        self.assertTrue(self.auth.get_token())
        self.assertTrue(self.auth.token)
        self.assertIsNone(self.auth.errors)

    def test_authentication_error(self):
        """Tests authentication errors"""
        auth = Authentication('test_error')
        self.assertIsNone(auth.errors)
        self.assertFalse(auth.get_token())
        self.assertTrue(auth.errors)
        self.assertIsNone(auth.token)

    def test_api_token_test(self):
        """Tests authentication test_api_token method"""
        self.assertTrue(self.auth.test_api_token())

    def test_api_get_roles(self):
        """Tests authentication api_get_roles method"""
        self.assertTrue(self.auth.get_roles())
        auth = Authentication(self.api_key)
        self.assertTrue(auth.get_roles())
        self.assertTrue(auth.token)
        self.assertIsNone(auth.errors)


class TestGeostoreRequest(TestCase):

    def setUp(self):
        self.geom = "POLYGON ((" \
            "-170.859375 -78.49055166160312," \
            " 191.25 -78.49055166160312," \
            " 191.25 84.86578186731522," \
            " -170.859375 84.86578186731522," \
            " -170.859375 -78.49055166160312))"
        self.api_key = os.getenv("TEST_API_KEY")
        self.geo_api = GeoApi(self.api_key)
        self.preview_url = "https://search.federated.geoapi-airbusds.com/" \
            "api/v1/productTypes/SPOTArchive1.5Mono/products/" \
            "DS_SPOT7_201801070929101_CB1_CB1_CB1_CB1_W021S78_01627" \
            "?size=LARGE"

    def test_get_headers(self):
        """Tests get headers private method for GeoAPI"""
        headers = self.geo_api._Api__get_authenticated_headers()
        self.assertTrue(headers)
        self.assertTrue(headers.get("Authorization"))

    def test_get_dates(self):
        """Tests get dates private method for GeoAPI"""
        dates = "2018-01-01", "2018-02-01"
        dates = self.geo_api._Api__get_dates(dates)
        self.assertTrue(dates)
        self.assertEquals(type(dates), str)
        self.assertEquals(dates, "[2018-01-01,2018-02-01[")

    def test_get_sort_keys(self):
        """Tests get sort keys private method for GeoAPI"""
        sort_keys = self.geo_api._Api__get_sort_keys()
        self.assertTrue(sort_keys)
        self.assertEquals(type(sort_keys), str)

    def test_get_coverage(self):
        """Tests get coverage str private method for GeoAPI"""
        coverage = self.geo_api._Api__get_less_than_or_equals(10)
        self.assertTrue(coverage)
        self.assertEquals(type(coverage), str)
        self.assertEquals(coverage, "10[")

    def test_get_geostore_url(self):
        """Tests get geostore url private method for GeoAPI"""
        geostore_url = self.geo_api.get_geostore_url()
        self.assertTrue(geostore_url)
        self.assertEquals(type(geostore_url), str)

    def test_get_payload_default_data(self):
        """Tests get payload dict method for GeoAPI with default data"""
        payload = self.geo_api.get_payload()
        self.assertTrue(payload)
        self.assertEquals(type(payload), dict)
        self.assertEquals(
            payload.get("sortKeys"),
            "sortKeys=acquisitionDate,,0")

    def test_get_payload_data_parameter(self):
        """Tests get payload dict method for GeoAPI with parameter data"""
        payload = self.geo_api.get_payload(sensorType="TEST")
        self.assertTrue(payload)
        self.assertEquals(type(payload), dict)
        self.assertEquals(payload.get("sensorType"), "TEST")

    def test_get_response_data_parameter(self):
        """Tests get response data method for GeoAPI"""
        payload = self.geo_api.get_payload(
            geometry=self.geom,
            acquisitionDates=["2020-01-01", "2020-02-01"],
            constellation=["SPOT"],
            cloudCover=10,
        )
        self.assertTrue(payload)
        self.assertEquals(type(payload), dict)
        self.assertTrue(payload.get("acquisitionDate"))
        response = self.geo_api.get_response_data(payload)
        self.assertEquals(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("totalResults"))
        self.assertTrue(data.get("startIndex"))
        self.assertTrue(data.get("itemsPerPage"))
        self.assertTrue(data.get("features"))
        self.assertEquals(data.get("itemsPerPage"), payload["count"])

        features = data.get("features")
        for feature in features:
            self.assertTrue(feature.get("geometry"))
            self.assertTrue(feature.get("quicklooks"))
            thumbnails = filter(
                lambda x: x.get("size") == "LARGE",
                feature.get("quicklooks")
            )
            thumbnails = next(thumbnails).get('image')
            self.assertTrue(thumbnails)

    def test_get_response_data_image_blob(self):
        """Tests get response image blob data method for GeoAPI"""
        thumbs = self.geo_api.get_image_data(self.preview_url)
        self.assertTrue(thumbs)

        thumbs = self.geo_api.get_image_data(self.preview_url + "err")
        self.assertIsNone(thumbs)

    def test_get_response_data_image_path(self):
        """Tests get response image path method for GeoAPI"""
        thumbs = self.geo_api.get_image_path(
            preview_url=self.preview_url
        )
        self.assertTrue(thumbs)
        self.assertTrue(os.path.exists(thumbs))

        thumbs = self.geo_api.get_image_path(
            preview_url=self.preview_url + "test"
        )
        self.assertIsNone(thumbs)

    def test_get_response_data_image_path_error(self):
        """Tests get response image path for GeoAPI with ValueError"""
        with self.assertRaises(ValueError):
            self.geo_api.get_image_path(
                feature=True,
                preview_url=self.preview_url
            )

    def test_get_response_data_image_path_feature(self):
        """
        Tests get response image path for GeoAPI with path from feature
        """
        payload = self.geo_api.get_payload(
            geometry=self.geom,
            acquisitionDates=["2020-01-01", "2020-02-01"],
            constellation=["PLEIADES"],
            cloudCover=10,
        )
        self.assertTrue(payload)
        self.assertEquals(type(payload), dict)
        self.assertTrue(payload.get("acquisitionDate"))

        response = self.geo_api.get_response_data(payload)
        data = response.json()
        thumbs = self.geo_api.get_image_path(
            feature=data.get("features")[0]
        )
        self.assertTrue(data)
        self.assertTrue(thumbs)
        self.assertEquals(response.status_code, 200)
