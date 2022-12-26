from . import auth


class AbstractApi:
    """AbstractAPI class to request data on Airbus endpoints."""

    def __init__(self, api_key: str) -> None:
        """Void method for class for Airbus API.

        Args:
            api_key (str): api_key created from
                https://account.foundation.oneatlas.airbus.com/
        """

        super(AbstractApi, self).__init__()
        self.api_key = api_key
        self.auth = auth.Authentication(api_key)
        self.auth.get_token()

        if not self.auth.errors:
            self.token = self.auth.token
        else:
            raise ValueError(str(self.auth.errors))

    def _get_included_values(self, value_list: list):
        """Gets included values parsing data from float to str.

        Internal method to return ranges expressed as follow:
            Comma to separate start value from end value
            Start value or end value can be omitted
                (it means values are infinite)
            Start with [ means start value is included
            Start with ] means start value is excluded
            End with [ means end value is included
            End with ] means end value is excluded

        Args:
            value_list (list): list with 2 values to create a filter data.

        Returns:
            data (str): string with brackets for filtering.
        """

        return '[{},{}['.format(*value_list)

    def _get_less_than_or_equals(self, value: float):
        """Gets less than or equal parsing data from float to str.

        Internal method to return ranges expressed as follow:
            Comma to separate start value from end value
            Start value or end value can be omitted
                (it means values are infinite)
            Start with [ means start value is included
            Start with ] means start value is excluded
            End with [ means end value is included
            End with ] means end value is excluded

        Args:
            value (float): float for filtering.

        Returns:
            str: string with brackets for filtering.
        """

        return '{}['.format(value)

    def _get_authenticated_headers(self) -> dict:
        """Gets authenticated headers with json content type.

        Authenticated headers for requests with Authorization 'Token Bearer'.

        Returns:
            dict: authorization header with bearer token
        """

        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
        }

    def _get_authenticated_headers_image(self) -> dict:
        """Gets authenticated headers for image without cache control.

        Authenticated headers for requests with Authorization 'Token Bearer'
        For Image requests without Content-Type attribute.

        Returns:
            dict: authorization header with bearer token.
        """

        return {
            'Authorization': f'Bearer {self.token}',
            'Cache-Control': 'no-cache'
        }
