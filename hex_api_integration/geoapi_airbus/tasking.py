import requests

from . import api


class Api(api.AbstractApi):
    """OneAtlas API class to request data on Airbus endpoints.

    Implements methods to request data for Tasking API following
    the documentation available in
    //api.oneatlas.airbus.com/guides/oneatlas-data-pay-per-order/g-tasking/.
    """

    def get_default_api_url(self) -> str:
        """Gets default API url for AirBus OneAtlas.

        Dafults url to: https://search.foundation.api.oneatlas.airbus.com

        Returns:
            str: Airbus default api url.
        """

        return 'https://search.foundation.api.oneatlas.airbus.com'

    def get_tasking_api_url(
        self,
        uri: str = '/api/v1/{cisContractId}/taskings'
    ) -> str:
        """Gets url for OneAtlas Tasking API search.

        Args:
            uri (str, optional): endpoint uri.
                Defaults to '/api/v1/{cisContractId}/taskings'.

        Returns:
            str: api tasking url.
        """

        return self.get_default_api_url() + uri

    def get_cis_contract_ids(self) -> list:
        """Gets cis contract ids from /api/v1/me endpoint.

        Returns:
            list: cis contract ids list.
        """

        contracts = self.auth.get_cis_contracts()

        if contracts['contracts']:
            return [ct.get('contractId') for ct in contracts['contracts']]

        return False

    def get_taskings_from_contract_ids(self) -> dict:
        """Get tasking list from contract ids.

        Returns:
            dict: contracts with list of taskings.
        """
        data = {}

        tasking_url = self.get_tasking_api_url()
        headers = self._get_authenticated_headers()

        for contract in self.get_cis_contract_ids():
            data[contract] = []
            response = requests.get(
                tasking_url.format(cisContractId=contract),
                headers=headers,
            )
            if response and response.ok():
                data[contract].append(response.json())

        return data
