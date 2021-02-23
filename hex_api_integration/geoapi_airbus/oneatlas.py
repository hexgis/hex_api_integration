import os
import json
import requests
import tempfile

from .api import AbstractApi


class Api(AbstractApi):

    def get_api_url(self):
        """
        Void method to get url for geostore API search

        Default url: https://authenticate.foundation.api.oneatlas.airbus.com/
            api/v1/opensearch
        """
        return "https://search.foundation.api.oneatlas.airbus.com" \
            "/api/v1/opensearch"

    def get_payload(
        self,
        bbox=[],
        geometry=None,
        acquisition_date_range=[],
        publication_date_range=[],
        cloud_cover=100,
        snow_cover=100,
        commercial_reference=None,
        constellation=[],
        incidence_angle=None,
        parent_idenfifier=None,
        platform=[],
        product_type=[],
        production_status=[],
        resolution=None,
        source_identifier=None,
        workspace=None,
        count=20,
        start_page=1,
        sort_key='-acquisitionDate,cloudCover',
    ):
        """
        Payload data object with user parameters

        Arguments:
            * bbox (list): list containing bbox data.
                Values are min lon, min lat, max lon, max lat.
            * geometry (list): WKT Geometry. Bbox and geometry
                could not be equals.
            * acquisition_date_range (list): acquisition dates.
            * cloud_cover (float): max cloud cover.
            * commercial_reference (str): commercial reference.
            * constellation (list): Constellation list.
                E.g.: ["PHR"] or ["PHR", "SPOT"]
            * incidence_angle (float): max incidencle angle.
            * parent_idenfifier (str): sourceId in other catalogs.
            * platform (list): Platform list names.
            * production_status (list): The production status list.
            * product_type (list): The product type list.
            * publication_date_range (list): Publication date range.
            * resolution (list): max resolution filter.
            * snow_cover (float): max snow cover.
            * source_identifier Nonetr): Product identifier.
            * workspace (str): Workspace id/name or workspace id/name list.
            * count (int): items per page.
            * start_page (int): data response page that request will start.
            * sort_by (str): sortKeys. Default: '-acquisitionDate,cloudCover'

        Returns:
            * payload (object): json object containing payload data
        """

        payload = {}
        payload["itemsPerPage"] = count
        payload["startPage"] = start_page
        payload["sortBy"] = sort_key

        if bbox:
            if type(bbox) == list or type(bbox) == tuple:
                payload["bbox"] = ",".join((str(point) for point in bbox))
            else:
                payload["bbox"] = bbox

        if geometry:
            payload["geometry"] = geometry

        if incidence_angle:
            value = self._get_less_than_or_equals(incidence_angle)
            payload["incidenceAngle"] = value

        if acquisition_date_range:
            dates = self._get_included_values(acquisition_date_range)
            payload["acquisitionDate"] = dates

        if publication_date_range:
            dates = self._get_included_values(publication_date_range)
            payload["publicationDate"] = dates

        if cloud_cover:
            payload["cloudCover"] = self._get_less_than_or_equals(cloud_cover)

        if snow_cover:
            payload["snowCover"] = self._get_less_than_or_equals(snow_cover)

        if commercial_reference:
            payload["commercialReference"] = commercial_reference

        if parent_idenfifier:
            payload["parentIdenfifier"] = parent_idenfifier

        if constellation and type(constellation) == list:
            payload["constellation"] = ",".join(constellation)

        if platform:
            payload["platform"] = ",".join(platform)

        if product_type:
            payload["productType"] = ",".join(product_type)

        if source_identifier:
            payload["sourceIdentifier"] = source_identifier

        if workspace:
            payload["workspace"] = workspace

        if production_status:
            payload["productionStatus"] = ",".join(production_status)

        if resolution:
            payload["resolution"] = self._get_less_than_or_equals(resolution)

        return payload

    def get_response_data(self, payload):
        """
        *Get data from api url*

        Requests data from OneAtlas API using authentication from
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
            headers=headers,
            verify=False
        )

        if response.ok:
            return response

        return None

    def get_image_data(self, preview_url):
        """
        *Get image data blob from feature image_url*

        Arguments:
            * preview_url (str): preview url for request

        Returns:
            * response (requests.response): a requests response data
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
        feature=None,
        preview_url=None,
    ):
        """
        *Get image path from feature image_url or preview_url*

        Arguments:
            * feature (dict): geojson feature data
            * preview_url (str): preview url data

        Returns:
            * path (str): path to image
        """

        error_msg = "Both feature and preview_url is not allowed"

        if feature and preview_url:
            raise ValueError(error_msg)

        if feature:
            preview_url = feature.get("_links").get("thumbnail")
            preview_url = preview_url.get("href")

        response = self.get_image_data(preview_url=preview_url)

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
