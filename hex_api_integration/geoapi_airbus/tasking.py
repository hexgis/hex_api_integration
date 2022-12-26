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
