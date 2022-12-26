import os
import json
import requests
import tempfile


from . import api


class Api(api.AbstractApi):
    """OneAtlas API class to request data on Airbus endpoints.

    Implements methods to request data for Geostore API following
    the documentation available in
    https://www.geoapi-airbusds.com/guides/oneatlas-data/g-search/.
    """

    def get_default_api_url(self) -> str:
        """Gets default API url for AirBus OneAtlas.

        Dafults url to: https://search.foundation.api.oneatlas.airbus.com

        Returns:
            str: Airbus default api url.
        """

        return 'https://search.foundation.api.oneatlas.airbus.com'

    def get_opensearch_api_url(self, uri: str = '/api/v2/opensearch') -> str:
        """Gets url for geostore API search.

        Args:
            uri (str, optional): endpoint uri.
                Defaults to '/api/v1/opensearch'.

        Returns:
            str: opensearch tasking url.
        """

        return self.get_default_api_url() + uri

    def get_wmts_service_url(self, EPSG: int = 3857) -> str:
        """Gets url for wmts service with default ESPG:3857.

        Args:
            EPSG (int, optional): Geodetic Parameter Dataset.
                Defaults to 3857.

        Returns:
            str: WMTS service url with configured EPSG.
        """

        return 'https://access.foundation.api.oneatlas.airbus.com/api/' \
            'v1/items/{id}/wmts/tiles/1.0.0/default/rgb/' \
            'EPSG' + str(EPSG) + '/{z}/{x}/{y}.png'

    def get_payload(
        self,
        bbox: list = [],
        geometry: str = None,
        acquisition_date_range: list = [],
        publication_date_range: list = [],
        cloud_cover: float = 100.0,
        snow_cover: float = 100.0,
        commercial_reference: str = None,
        constellation: list = ['PHR', 'SPOT', 'PNEO'],
        incidence_angle: str = None,
        parent_idenfifier: str = None,
        platform: list = [],
        product_type: list = [],
        production_status: list = [],
        resolution: float = None,
        source_identifier: str = None,
        workspace: str = None,
        processing_level: list = ['SENSOR', 'ALBUM'],
        count: int = 20,
        start_page: int = 1,
        sort_key: str = '-acquisitionDate,cloudCover',
    ):
        """Gets payload data object with user parameters.

        Args:
            bbox (list): list containing bbox data.
                Values are min lon, min lat, max lon, max lat.
            geometry (list): WKT Geometry. Bbox and geometry
                could not be equals.
            acquisition_date_range (list): acquisition dates.
            cloud_cover (float): max cloud cover.
            commercial_reference (str): commercial reference.
            constellation (list): Constellation list.
                E.g.: ['PHR'] or ['PHR', 'SPOT']
            incidence_angle (float): max incidencle angle.
            parent_idenfifier (str): sourceId in other catalogs.
            platform (list): Platform list names.
            production_status (list): The production status list.
            product_type (list): The product type list.
            publication_date_range (list): Publication date range.
            resolution (list): max resolution filter.
            snow_cover (float): max snow cover.
            source_identifier (str): Product identifier.
            workspace (str): Workspace id/name or workspace id/name list.
            processing_level (list): Processing Level.
                E.g.: ['SENSOR', 'ALBUM']
            count (int): items per page.
            start_page (int): data response page that request will start.
            sort_by (str): sortKeys. Default: '-acquisitionDate,cloudCover'.

        Returns:
            dict: json object containing payload data.
        """

        payload = {}
        payload['itemsPerPage'] = count
        payload['startPage'] = start_page
        payload['sortBy'] = sort_key

        if bbox:
            if type(bbox) == list or type(bbox) == tuple:
                payload['bbox'] = ','.join((str(point) for point in bbox))
            else:
                payload['bbox'] = bbox

        if geometry:
            payload['geometry'] = geometry

        if incidence_angle:
            value = self._get_less_than_or_equals(incidence_angle)
            payload['incidenceAngle'] = value

        if acquisition_date_range:
            dates = self._get_included_values(acquisition_date_range)
            payload['acquisitionDate'] = dates

        if publication_date_range:
            dates = self._get_included_values(publication_date_range)
            payload['publicationDate'] = dates

        if cloud_cover:
            payload['cloudCover'] = self._get_less_than_or_equals(cloud_cover)

        if snow_cover:
            payload['snowCover'] = self._get_less_than_or_equals(snow_cover)

        if commercial_reference:
            payload['commercialReference'] = commercial_reference

        if parent_idenfifier:
            payload['parentIdenfifier'] = parent_idenfifier

        if constellation and type(constellation) == list:
            payload['constellation'] = ','.join(constellation)

        if platform:
            payload['platform'] = ','.join(platform)

        if product_type:
            payload['productType'] = ','.join(product_type)

        if source_identifier:
            payload['sourceIdentifier'] = source_identifier

        if workspace:
            payload['workspace'] = workspace

        if processing_level:
            payload['processingLevel'] = ','.join(processing_level)

        if production_status:
            payload['productionStatus'] = ','.join(production_status)

        if resolution:
            payload['resolution'] = self._get_less_than_or_equals(resolution)

        return payload

    def get_response_data(self, payload: dict) -> requests.Response:
        """Gets reponse data from OneAtlas API.

        Requests data from OneAtlas API using authentication from
        geoapi_airbus.Authentication. Uses filters from payload data request
        returning requests response object.

        Args:
            payload (dict): payload data for filtered request.

        Returns:
            requests.Response: a requests response data.
        """

        headers = self._get_authenticated_headers()
        payload = json.dumps(payload)
        response = requests.post(
            self.get_opensearch_api_url(),
            data=payload,
            headers=headers
        )

        return response

    def get_image_data(self, preview_url) -> requests.Response:
        """Gets image data blob from feature image_url.

        Args:
            preview_url (str): preview url for request.

        Returns:
            requests.Response: a requests response data.
        """

        headers = self._get_authenticated_headers_image()
        response = requests.get(
            preview_url,
            headers=headers,
        )

        if response and response.ok:
            return response

        return None

    def get_image_path(
        self,
        feature: dict = None,
        preview_url: str = None,
    ):
        """Gets image path from feature image_url or preview_url.

        Args:
            feature (dict): geojson feature data.
            preview_url (str): preview url data.

        Returns:
            str: path to downloaded image.
        """

        if feature and preview_url:
            raise ValueError('Both feature and preview_url is not allowed')

        if feature:
            preview_url = feature.get('_links').get('thumbnail')
            preview_url = preview_url.get('href')

        response = self.get_image_data(preview_url=preview_url)

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

    def get_wmts_image_data(
        self,
        id: str,
        z: int,
        x: int,
        y: int
    ) -> requests.Response:
        """Get wmts image data for each zxy request.

        Returns image content for grid system as requests.Response instance.

        Args:
            id (str): Airbus OneAtlas data id.
            z (int): zoom level.
            x (int): x position in grid.
            y (int): y position in grid.

        Returns:
            requests.Response: response data.
        """

        url = self.get_wmts_service_url()
        url = url.format(id=id, z=str(z), x=str(x), y=str(y))

        return self.get_image_data(url)

    def get_data_usage(self) -> requests.models.Response:
        """Get amount of data used on all subscriptions.

        It mappes between all subcriptions and returns the first one that
        has consumed amount and max amount of data in it.

        Returns:
            requests.models.Response: Returns data with either the consumed
                and max amount of an error message.
        """

        response = requests.models.Response()

        try:
            consumed_value, max_value = self.auth.get_usage()
            data = {'consumed': consumed_value, 'max': max_value}

            response.status_code = 200
            response._content = json.dumps(data).encode('utf-8')
        except Exception as exc:
            data = {
                'error': 'no_limited_subscriptions',
                'error_description': str(exc)
            }
            response.status_code = 404
            response._content = json.dumps(data).encode('utf-8')

        return response
