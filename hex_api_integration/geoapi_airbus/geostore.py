import os
import json
import requests
import tempfile

from .auth import Authentication


class Api:

    def __init__(self, api_key):
        """
        Api class for GeoStore from airbus

        Arguments:
            * api_key (str): api_key created from
                https://account.foundation.oneatlas.airbus.com/
        """
        super(Api, self).__init__()
        self.api_key = api_key
        self.auth = Authentication(api_key)
        self.auth.get_token()

        if not self.auth.errors:
            self.token = self.auth.token
        else:
            raise ValueError(str(self.auth.errors))

    def __get_authenticated_headers(self):
        """
        Authenticated headers for requests with Authorization 'Token Bearer'

        Returns:
            * header (object): authorization header with bearer token
        """
        return {
            'Authorization': "Bearer {}".format(self.token),
            'Content-Type': "application/json",
            'Cache-Control': "no-cache",
        }

    def __get_authenticated_headers_image(self):
        """
        Authenticated headers for requests with Authorization 'Token Bearer'
        For Image requests without Content-Type attribute

        Returns:
            * header (object): authorization header with bearer token
        """

        return {
            'Authorization': "Bearer {}".format(self.token),
            'Cache-Control': "no-cache"
        }

    def __get_dates(self, date_list):
        return "[{},{}[".format(*date_list)

    def __get_less_than_or_equals(self, data):
        return "{}[".format(data)

    def __get_sort_keys(self):
        return "sortKeys=acquisitionDate,,0"

    def get_geostore_url(self):
        """
        Void method to get url for geostore API search

        Default url https://search.federated.geoapi-airbusds.com/api/v1/search
        """

        return "https://search.federated.geoapi-airbusds.com/api/v1/search"

    def get_payload(
        self,
        bbox=[],
        constellation=[],
        acquisitionDates=[],
        polarisationChannels=[],
        productType=[],
        resolution=None,
        geometry=None,
        cloudCover=None,
        snowCover=None,
        incidenceAngle=None,
        sensorType=None,
        antennaLookDirection=None,
        orbitDirection=None,
        count=20,
        startPage=1,
    ):
        """
        Payload data object with user parameters

        Arguments:
            * bbox (list): list containing bbox data
            * constellation (list): list of constellation
            * acquisitionDates (list): acquisition dates
            * polarisationChannels (list): list of polarisation channels
            * productType (list): list of product types
            * geometry (list): WKT Geometry. Bbox and geometry
                could not be equals.
            * resolution (list): maximum resolution filter
            * cloudCover (list): maximum cloud cover
            * snowCover (list):  maximum snow cover
            * incidenceAngle (list): list of image incidence angle
            * sensorType (list): list of sensors
            * antennaLookDirection (list): list of antenna look direction
            * orbitDirection (list): list of orbit direction
            * count (int): data count per request
            * startPage (int): which data response page will start

        Returns:
            * payload (object): json object containing payload data
        """
        payload = {}
        payload["count"] = count
        payload["startPage"] = 1
        payload["sortKeys"] = self.__get_sort_keys()

        if geometry:
            payload["geometry"] = geometry

        if bbox:
            payload["bbox"] = bbox

        if constellation:
            payload["constellation"] = constellation

        if acquisitionDates:
            dates = self.__get_dates(acquisitionDates)
            payload["acquisitionDate"] = dates

        if polarisationChannels:
            payload["polarisationChannels"] = polarisationChannels

        if productType:
            payload["productType"] = productType

        if resolution:
            payload["resolution"] = self.__get_less_than_or_equals(resolution)

        if cloudCover:
            payload["cloudCover"] = self.__get_less_than_or_equals(cloudCover)

        if snowCover:
            payload["snowCover"] = self.__get_less_than_or_equals(snowCover)

        if incidenceAngle:
            incidenceAngle = self.__get_less_than_or_equals(incidenceAngle)
            payload["incidenceAngle"] = incidenceAngle

        if sensorType:
            payload["sensorType"] = sensorType

        if antennaLookDirection:
            payload["antennaLookDirection"] = antennaLookDirection

        if orbitDirection:
            payload["orbitDirection"] = orbitDirection

        if count:
            payload["count"] = count

        if startPage:
            payload["startPage"] = startPage

        return payload

    def get_response_data(self, payload):
        """
        *Get data from geostore url*

        Requests data from GeoStore API using authentication from
        geoapi_airbus.Authentication. Uses filters from payload data requesting
        data and returning requests response data

        Arguments:
            * payload (dict): payload data for filtered request

        Returns:
            * response (requests.response): a requests response data
        """

        headers = self.__get_authenticated_headers()
        payload = json.dumps(payload)
        response = requests.post(
            self.get_geostore_url(),
            data=payload,
            headers=headers
        )

        if response.ok:
            return response

        return None

    def get_image_data(self, preview_url, img_size="LARGE"):
        """
        *Get image data blob from feature image_url*

        Arguments:
            * preview_url (str): preview url for request
            * img_size (str): image size.
                Could be: 'SMALL', 'MEDIUM', 'LARGE'

        Returns:
            * response (requests.response): a requests response data
        """

        headers = self.__get_authenticated_headers_image()
        payload = {"size": img_size}
        response = requests.get(
            preview_url,
            headers=headers,
            params=json.dumps(payload)
        )

        if response and response.ok:
            return response

        return None

    def get_image_path(
        self,
        feature=None,
        preview_url=None,
        img_size="LARGE"
    ):
        """
        *Get image path from feature image_url or preview_url*

        Arguments:
            * feature (dict): geojson feature data
            * preview_url (str): preview url data
            * img_size (str): image size.
                Could be: 'SMALL', 'MEDIUM', 'LARGE'

        Returns:
            * path (str): path to image
        """

        error_msg = "Both feature and preview_url is not allowed"

        if feature and preview_url:
            raise ValueError(error_msg)

        if feature:
            thumbnails = filter(
                lambda x: x.get("size") == img_size,
                feature.get("quicklooks")
            )
            thumbnails = next(thumbnails).get('image')
            response = self.get_image_data(
                preview_url=thumbnails, img_size=img_size)
        else:
            response = self.get_image_data(
                preview_url=preview_url, img_size=img_size)

        if response and response.ok:
            temp_path = os.path.join(
                tempfile._get_default_tempdir(),
                next(tempfile._get_candidate_names()) + ".jpg"
            )
            try:
                with open(temp_path, "wb") as f:
                    f.write(response.content)
                    f.close()
                return temp_path
            except Exception as exc:
                raise ValueError("Error while writing image: {}".format(exc))

        return None
