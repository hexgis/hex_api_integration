import os
import json
import requests
import tempfile

from . import api


class Api(api.AbstractApi):
    """Geostore API class to request data on Airbus endpoints.

    Implements methods to request data for Geostore API following
    the documentation available in
    https://geoapi-airbusds.com/guides/oneatlas-data-pay-per-order/g-tasking/.
    """

    def get_sort_keys(self, sort_key: str = "-date") -> str:
        """Get keys to use on sort;

        Args:
            sort_key (str, optional): sort key.
                Defaults to "-date".

        Returns:
            str: sort method.
        """

        key = 'acquisitionDate'
        order = '1'

        if sort_key and len(sort_key):
            if sort_key[0] == '-':
                order = '0'
                sort_key = sort_key[1:]
            if sort_key == 'date':
                key = 'acquisitionDate'
            elif sort_key == 'cloud_rate':
                key = 'cloudCover'

        return '{},,{}'.format(key, order)

    def get_search_api_url(self) -> str:
        """ Void method to get url for geostore API search.

        Default url to
        https://search.federated.geoapi-airbusds.com/api/v1/search

        Returns:
            str: Geostore Search API Url.
        """

        return 'https://search.federated.geoapi-airbusds.com/api/v1/search'

    def get_payload(
        self,
        bbox: list = [],
        constellation: list = [],
        acquisition_date_range: list = [],
        polarisation_channels: list = [],
        product_type: list = [],
        resolution: str = None,
        geometry: str = None,
        cloud_cover: float = None,
        snow_cover: float = None,
        incidence_angle: float = None,
        sensor_type: str = None,
        antenna_look_direction: str = None,
        orbit_direction: str = None,
        count: int = 20,
        start_page: int = 1,
        sort_key: str = '-date',
    ) -> dict:
        """
        Payload data object with user parameters

        Args:
            bbox (list): list containing bbox data.
            constellation (list): list of constellation.
            acquisition_date_range (list): acquisition dates.
            polarisation_channels (list): list of polarisation channels.
            product_type (list): list of product types.
            geometry (str): WKT Geometry.
                Bbox and geometry could not be equals.
            resolution (str): maximum resolution filter.
            cloud_cover (str): maximum cloud cover.
            snow_cover (str):  maximum snow cover.
            incidence_angle (str): list of image incidence angle.
            sensor_type (str): list of sensors.
            antenna_look_direction (str): list of antenna look direction.
            orbit_direction (str): list of orbit direction.
            count (int): data count per request.
            start_page (int): which data response page will start.
            sort_key (str): sort method. Defaults to '-date'.

        Returns:
            dict: json object containing payload data.
        """
        payload = {}
        payload['count'] = count
        payload['startPage'] = 1
        payload['sortKeys'] = self.get_sort_keys(sort_key)

        if geometry:
            payload['geometry'] = geometry

        if bbox:
            payload['bbox'] = bbox

        if constellation:
            payload['constellation'] = constellation

        if acquisition_date_range:
            dates = self._get_included_values(acquisition_date_range)
            payload['acquisitionDate'] = dates

        if polarisation_channels:
            payload['polarisationChannels'] = polarisation_channels

        if product_type:
            payload['productType'] = product_type

        if resolution:
            payload['resolution'] = self._get_less_than_or_equals(resolution)

        if cloud_cover:
            payload['cloudCover'] = self._get_less_than_or_equals(cloud_cover)

        if snow_cover:
            payload['snowCover'] = self._get_less_than_or_equals(snow_cover)

        if incidence_angle:
            incidence_angle = self._get_less_than_or_equals(incidence_angle)
            payload['incidenceAngle'] = incidence_angle

        if sensor_type:
            payload['sensorType'] = sensor_type

        if antenna_look_direction:
            payload['antennaLookDirection'] = antenna_look_direction

        if orbit_direction:
            payload['orbitDirection'] = orbit_direction

        if count:
            payload['count'] = count

        if start_page:
            payload['startPage'] = start_page

        return payload

    def get_response_data(self, payload: dict) -> requests.Response:
        """Gets data from geostore url.

        Requests data from GeoStore API using authentication from
        geoapi_airbus.Authentication. Uses filters from payload data request
        returning requests response object

        Args:
            payload (dict): payload data for filtered request

        Returns:
            requests.Response: a requests response data.
        """

        headers = self._get_authenticated_headers()
        payload = json.dumps(payload)
        response = requests.post(
            self.get_search_api_url(),
            data=payload,
            headers=headers
        )

        if response.ok:
            return response

        return None

    def get_image_data(
        self,
        preview_url: str,
        img_size: str = 'LARGE'
    ) -> requests.Response:
        """Gets image data blob from feature image_url.

        Args:
            preview_url (str): preview url for request
            img_size (str): image size. Could be: 'SMALL', 'MEDIUM', 'LARGE'.
                Defaults to 'LARGE'.

        Returns:
            requests.Response: a requests response data
        """

        headers = self._get_authenticated_headers_image()
        payload = {'size': img_size}
        response = requests.get(
            preview_url,
            headers=headers,
            params=json.dumps(payload)
        )

        return response

    def get_image_path(
        self,
        feature: dict = None,
        preview_url: str = None,
        img_size: str = 'LARGE'
    ) -> str:
        """Gets image path from feature image_url or preview_url

        Args:
            feature (dict): geojson feature data
            preview_url (str): preview url data
            img_size (str): image size. Could be: 'SMALL', 'MEDIUM', 'LARGE'.
                Defaults to 'LARGE'.

        Returns:
            str: path to downloaded image.
        """

        if feature and preview_url:
            raise ValueError('Both feature and preview_url is not allowed')

        if feature:
            thumbnails = filter(
                lambda x: x.get('size') == img_size,
                feature.get('quicklooks')
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
                next(tempfile._get_candidate_names()) + '.jpg'
            )
            try:
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                    f.close()
                return temp_path
            except Exception as exc:
                raise ValueError(f'Error while writing image: {exc}')

        return None
