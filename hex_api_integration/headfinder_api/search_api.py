import os
import json
import requests
import tempfile
import urllib.parse


class Api():

    def __init__(self, user_key: str):
        """Api class for HEADFinder API.

        Args:
            user_key (str): user key acquired from HEAD
        """
        self.user_key = user_key

    def get_search_api_url(self) -> str:
        """Get HEADFinder Search API URL.

        Returns:
            str: HEADFinder Search API URL
        """
        return 'https://headfinder.head-aerospace.eu/search-ext-01/'

    def get_preview_api_url(self) -> str:
        """Get HEADFinder Preview API URL.

        Returns:
            str: HEADFinder Preview API URL
        """
        return 'https://headfinder.head-aerospace.eu/api-01/'

    def get_payload(
        self,
        bbox: list = None,
        geometry: list = None,
        satellites: list = None,
        scene_id: str = None,
        scene_id_exact_match: bool = True,
        max_scenes: int = 50,
        start_date: str = None,
        end_date: str = None,
        cloud_cover: int = 100,
        incidence_angle: int = 60,
    ) -> dict:
        """Get payload data object with user parameters.

        Args:
            bbox (list, optional):
                Bounding box of AOI. Defaults to None.
            geometry (list, optional):
                AOI in WKT polygon format. Defaults to None.
            satellites (list, optional):
                List of HEAD satellites. Defaults to None.
            scene_id (str, optional):
                Scene name. Defaults to None.
            scene_id_exact_match (bool, optional):
                Match name exactly if true, partially if false.
                Defaults to True.
            max_scenes (int, optional):
                Max number of scenes to return. Limited to 50. Defaults to 50.
            start_date (str, optional):
                Start date in YYYY-MM-DD format. Defaults to None.
            end_date (str, optional):
                End date in YYYY-MM-DD format. Defaults to None.
            cloud_cover (int, optional):
                Max percent cloud cover. Defaults to 100.
            incidence_angle (int, optional):
                Max percent of incidence angle. Defaults to 60.

        Returns:
            dict: payload data object
        """
        payload = {}
        payload['req'] = 'd01'
        payload['category'] = 'searchapi-01'
        payload['user'] = self.user_key
        payload['overlapmin'] = 10

        if geometry:
            payload['aoi'] = geometry
        elif bbox:
            payload['aoi'] = \
                f'rectangle(({bbox[1]},{bbox[0]}),({bbox[3]},{bbox[2]}))'

        if satellites:
            satellites = '$'.join(satellites)
            payload['satellites'] = f'${satellites}$'
        else:
            satellites = '$SuperView$EarthScanner-KF1$'

        if scene_id:
            payload['scenename'] = scene_id

        if scene_id_exact_match is None or scene_id_exact_match is True:
            payload['scenenamematch'] = 'exact'
        else:
            payload['scenenamematch'] = 'partial'

        if max_scenes and max_scenes <= 50:
            payload['maxscenes'] = max_scenes
        else:
            payload['maxscenes'] = 50

        if start_date:
            payload['datestart'] = start_date

        if end_date:
            payload['dateend'] = end_date

        if cloud_cover:
            payload['cloudmax'] = cloud_cover

        if incidence_angle:
            payload['offnadirmax'] = incidence_angle

        return payload

    def get_response_data(
        self,
        payload: dict
    ) -> 'requests.Response':
        """Get data from search api url.

        Requests data from HEADFinder Search API.
        Uses filters from payload data request
        and returns requests response object

        Args:
            payload (dict): payload data for filtered request

        Returns:
            requests.Response: response data
        """
        payload = urllib.parse.urlencode(payload, safe=',$()')
        response = requests.get(
            self.get_search_api_url(),
            params=payload
        )

        if response.ok:
            return response
        response.raise_for_status()

    def get_image_payload(self,
        scene_id: str,
        img_quality: str = 'max'
    ) -> dict:
        """Get scene preview request params payload

        Args:
            scene_id (str): scene ID.
            img_quality (str, optional): image quality, either low, std or max.
                Defaults to 'max'.

        Returns:
            dict: payload data
        """
        payload = {}
        payload['req'] = 'd01'
        payload['category'] = 'getpreview-01'
        payload['user'] = self.user_key
        payload['imgformat'] = 'png'
        payload['scenenamematch'] = 'exact'

        if scene_id:
            payload['scenename'] = scene_id

        if img_quality:
            payload['imgquality'] = img_quality

        return payload

    def get_image_data(
        self,
        payload: dict
    ) -> 'requests.Response':
        """Get image data blob for specified scene id

        Args:
            payload (dict): payload data containing scene ID

        Returns:
            requests.Response: response data containing image in PNG format
        """
        response = requests.get(
            self.get_preview_api_url(),
            params=payload
        )

        if response.ok:
            return response
        response.raise_for_status()
