import requests


class Authentication:

    def __init__(self, api_key):
        """
        Authentication class for geoapi from airbus

        Arguments:
            * api_key (str): api_key created from
                https://account.foundation.oneatlas.airbus.com/
        """

        self.api_key = api_key
        self.url = "https://authenticate.foundation" \
            ".api.oneatlas.airbus.com/auth/" \
            "realms/IDP/protocol/openid-connect/token"
        self.token = None
        self.errors = None

    def __get_headers(self):
        """
        Headers for api requests with Content Type and Cache-Control data

        Returns:
            * header (object): Content-Type and Cache-Control data
        """

        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': "no-cache",
        }

    def __get_auth_headers(self):
        """
        Authenticated headers for requests with Authorization 'Token Bearer'

        Returns:
            * header (object): authorization header with bearer token
        """

        return {
            "Authorization": "Bearer {}".format(self.token)
        }

    def __get_data(self, api_key):
        """
        Data for requests with api_key data, grant_type and client_id

        Arguments:
            * api_key (bool): api_key created from
                https://account.foundation.oneatlas.airbus.com/

        Returns:
            * data (list): api data for requests
        """

        return [
            ('apikey', api_key),
            ('grant_type', 'api_key'),
            ('client_id', 'IDP'),
        ]

    def get_token(self):
        """
        **Geo API get authentication data**

        Get token from Authentication.url data to token data
        Available on Authentication.token

        Returns:
            * availability (bool): user authenticated
        """

        response = requests.post(
            self.url,
            headers=self.__get_headers(),
            data=self.__get_data(self.api_key)
        )

        if response.status_code == 403:
            self.errors = response.json()
            return None

        response_obj = response.json()
        self.token = response_obj.get('access_token')

        return True

    def test_api_token(self):
        """
        **Geo API get authentication data**

        Will test user api token availability from openid-connect/token from
        auth/realms/IDP/protocol/openid-connect/token/auth/realms/IDP/protocol

        Returns:
            * availability (bool): user is still authenticated
        """

        url = "https://authenticate.foundation.api.oneatlas.airbus.com/" \
            "auth/realms/IDP/protocol/openid-connect/token/auth/realms/" \
            "IDP/protocol/openid-connect/token"

        payload = "grant_type=api_key&client_id=AAA&apikey=" + self.api_key
        response = requests.post(
            url,
            data=payload,
            headers=self.__get_headers()
        )

        if response.status_code == 403:
            self.errors = response.json()
            return None

        return True

    def get_roles(self):
        """
        **Geo API get roles data**

        Will get roles from api/vi/me/services available for user

        Returns:
            * roles (object): rules available for user
        """

        if not self.token:
            token = self.get_token()
            if not token:
                return False

        url = "https://data.api.oneatlas.airbus.com/api/v1/me/services"
        response = requests.get(
            url,
            headers=self.__get_auth_headers()
        )

        if response.status_code == 403:
            return False

        return response.json()


    def get_me(self) -> object:
        """
        **Geo API get me data**

        Will get user info from api/vi/me

        Returns:
            *  (object): user information
        """
        if not self.token:
            token = self.get_token()
            if not token:
                return False

        url = "https://data.api.oneatlas.airbus.com/api/v1/me"
        response = requests.get(url, headers=self.__get_auth_headers())

        if response.status_code == 403:
            return False

        return response.json()

    def get_contract_id(self) -> str:
        user_info = self.get_me()

        if (
            not user_info
            or not user_info["contract"]
            or not user_info["contract"]["id"]
        ):
            return None

        return user_info["contract"]["id"]

    def __get_all_subscription_url(self, contract_id):
        return (
            f"https://data.api.oneatlas.airbus.com/api/v1/contracts"
            f"/{contract_id}/subscriptions"
        )

    def get_all_subscriptions(self):
        if not self.token:
            token = self.get_token()
            if not token:
                return False

        url = self.__get_all_subscription_url(self.get_contract_id())
        response = requests.get(url, headers=self.__get_auth_headers())

        if response.status_code == 403:
            return False

        return response.json()

    def get_usage(self):
        user_subscriptions = self.get_all_subscriptions()
        subscriptions = user_subscriptions["items"]

        if len(subscriptions):
            for subscription in subscriptions:
                if subscription["amountConsumed"] and subscription["amountMax"]:
                    return [subscription["amountConsumed"], subscription["amountMax"]]

        return [None, None]
