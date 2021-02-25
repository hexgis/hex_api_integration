import os
import json
import requests
import tempfile

from .api import AbstractApi


class Api(AbstractApi):

    def __get_sort_keys(self, sort_key="-date"):
        key = "acquisitionDate"
        order = "1"
        if sort_key and len(sort_key):
            if sort_key[0] == "-":
                order = "0"
                sort_key = sort_key[1:]
            if sort_key == "date":
                key = "acquisitionDate"
            elif sort_key == "cloud_rate":
                key = "cloudCover"

        return "{},,{}".format(key, order)

    def get_api_url(self):
        """
        Void method to get url for geostore API search

        Default url https://search.federated.geoapi-airbusds.com/api/v1/search
        """

        return "https://search.federated.geoapi-airbusds.com/api/v1/search"

    def get_payload(
        self,
        bbox=[],
        constellation=[],
        acquisition_date_range=[],
        polarisation_channels=[],
        product_type=[],
        resolution=None,
        geometry=None,
        cloud_cover=None,
        snow_cover=None,
        incidence_angle=None,
        sensor_type=None,
        antenna_look_direction=None,
        orbit_direction=None,
        count=20,
        start_page=1,
        sort_key='-date',
    ):
        """
        Payload data object with user parameters

        Arguments:
            * bbox (list): list containing bbox data
            * constellation (list): list of constellation
            * acquisition_date_range (list): acquisition dates
            * polarisation_channels (list): list of polarisation channels
            * product_type (list): list of product types
            * geometry (list): WKT Geometry. Bbox and geometry
                could not be equals.
            * resolution (list): maximum resolution filter
            * cloud_cover (list): maximum cloud cover
            * snow_cover (list):  maximum snow cover
            * incidence_angle (list): list of image incidence angle
            * sensor_type (list): list of sensors
            * antenna_look_direction (list): list of antenna look direction
            * orbit_direction (list): list of orbit direction
            * count (int): data count per request
            * start_page (int): which data response page will start

        Returns:
            * payload (object): json object containing payload data
        """
        payload = {}
        payload["count"] = count
        payload["startPage"] = 1
        payload["sortKeys"] = self.__get_sort_keys(sort_key)

        if geometry:
            payload["geometry"] = geometry

        if bbox:
            payload["bbox"] = bbox

        if constellation:
            payload["constellation"] = constellation

        if acquisition_date_range:
            dates = self._get_included_values(acquisition_date_range)
            payload["acquisitionDate"] = dates

        if polarisation_channels:
            payload["polarisationChannels"] = polarisation_channels

        if product_type:
            payload["productType"] = product_type

        if resolution:
            payload["resolution"] = self._get_less_than_or_equals(resolution)

        if cloud_cover:
            payload["cloudCover"] = self._get_less_than_or_equals(cloud_cover)

        if snow_cover:
            payload["snowCover"] = self._get_less_than_or_equals(snow_cover)

        if incidence_angle:
            incidence_angle = self._get_less_than_or_equals(incidence_angle)
            payload["incidenceAngle"] = incidence_angle

        if sensor_type:
            payload["sensorType"] = sensor_type

        if antenna_look_direction:
            payload["antennaLookDirection"] = antenna_look_direction

        if orbit_direction:
            payload["orbitDirection"] = orbit_direction

        if count:
            payload["count"] = count

        if start_page:
            payload["startPage"] = start_page

        return payload

    def get_response_data(self, payload):
        """
        *Get data from geostore url*

        Requests data from GeoStore API using authentication from
        geoapi_airbus.Authentication. Uses filters from payload data request
        returning requests response object

        Arguments:
            * payload (dict): payload data for filtered request

        Returns:
            * response (requests.response): a requests response data
        """

        headers = self._get_authenticated_headers()
        payload = json.dumps(payload)
        response = requests.post(
            self.get_api_url(),
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

        headers = self._get_authenticated_headers_image()
        payload = {"size": img_size}
        response = requests.get(
            preview_url,
            headers=headers,
            params=json.dumps(payload)
        )

        return response

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
