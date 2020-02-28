# In my opinion, Offers connector should be separated module in own repository,
# but I think that this is beyond assignment.
# Separation have this benefits:
# * Version of connector can be tagged in repository and older version can be used if older version of
#   offers service deployed somewhere.
# * This code can be simply reused in another project.
import requests
from typing import Tuple, List, Dict, Callable
from os import getenv

# URL
BASE_URL = getenv('OffersMS_BaseUrl')
BASE_URL = 'https://applifting-python-excercise-ms.herokuapp.com/api/v1' if BASE_URL is None else BASE_URL
AUTH_SUB_URL = '/auth'
AUTH_URL = BASE_URL + AUTH_SUB_URL
PRODUCT_REGISTER_SUB_URL = '/products/register'
PRODUCT_REGISTER_URL = BASE_URL + PRODUCT_REGISTER_SUB_URL
PRODUCT_OFFERS_SUB_URL = '/products/{prod_id}/offers'
PRODUCT_OFFERS_URL = BASE_URL + PRODUCT_OFFERS_SUB_URL

# offers API Values
ACCESS_TOKEN = 'access_token'
ERROR_CODE = 'code'
ERROR_MESSAGE = 'msq'


class OffersConnector:

    # EXCEPTIONS
    class EOffersConnector(Exception):
        """ Common Exception for OffersConnector class. """

    class EConnection(EOffersConnector):
        """ Exceptions corresponding with connection to service. """

    class ENoAuth(EConnection):
        """ Offers service need simple authentication. Call OffersConnector.auth() before any action. """
        def __init__(self, url: str):
            self.msg = '{url} - no authentication.'.format(url=url)

    class ERequestException(EConnection):
        """ Exception during connection to Offers service """
        def __init__(self, url: str, original_exception: Exception):
            self.msg = '{url} - Exception during request:\n{e}'.format(url=url, e=original_exception)
            self.original_exception = original_exception

    class EResponseValidation(EOffersConnector):
        """ Exception corresponding with invalid response. e.g. Service return Not Found. """

    class EInvalidJSONResponse(EResponseValidation):
        """ Offers service returned invalid json. """
        def __init__(self, url: str, code: int, raw_response: str, original_exception: Exception):
            msg = '{url} - Invalid JSON Response(code:{code}):\n{raw_response}\noriginal exception:\n' \
                       '{original_exception}\n'
            self.msg = msg.format(url=url, code=code, raw_response=raw_response, original_exception=original_exception)

    class EUnexpectedResponse(EResponseValidation):
        """ Offers service return response which is invalid. Probably edit of OfferConnector.py is needed due to changes
        at Offers service side. """
        def __init__(self, url: str, code: int, json: dict):
            self.msg = '{url} - Unexpected response code({code}):\n{json}'.format(url=url, code=code, json=json)

    class ECannotParseToken(EResponseValidation):
        """ During authentication was returned unexpected response. Probably edit of OfferConnector.py is needed due to
        changes at Offers service side. """
        def __init__(self, url: str, json: dict):
            self.msg = '{url} - Cannot parse token in:\n {json}'.format(url=url, json=json)

    class EExpectedErrorResponse(EResponseValidation):
        """ Expected response, but invalid. e.g. Service return Not Found. """

        def __init__(self, url: str, code: int, msg: str):
            self.msg = '{url} - {code} - {msg}'.format(url=url, code=code, msg=msg)
            self.response_code = code
            self.message = msg

        @staticmethod
        def make_descendant(url: str, code: int, msg: str):
            if code == 400:
                return OffersConnector.EBadRequest(url, code, msg)
            elif code == 401:
                return OffersConnector.EUnauthorized(url, code, msg)
            elif code == 404:
                return OffersConnector.ENotFound(url, code, msg)

    class EBadRequest(EExpectedErrorResponse):
        """ Offers Service returned bad request. """

    class EUnauthorized(EExpectedErrorResponse):
        """ Offers Service returned unauthorized. """

    class ENotFound(EExpectedErrorResponse):
        """ Offers Service returned not found. """

    # CLASS METHODS

    def __init__(self, load_token: Callable[[], str], save_token: Callable[[str], None]):
        self.access_token = load_token()
        if self.access_token is None:
            save_token(self.auth())

    def auth(self) -> str:
        r, json = self._call(url=AUTH_URL, sub_url=AUTH_SUB_URL, post=True)

        if r.status_code != 201:
            raise OffersConnector.EUnexpectedResponse(AUTH_URL, r.status_code, json)

        if ACCESS_TOKEN not in json:
            raise OffersConnector.ECannotParseToken(url=AUTH_URL, json=json)

        self.access_token = json[ACCESS_TOKEN]
        return self.access_token

    def product_register(self, prod_id: int, name: str, desc: str) -> None:
        r, json = self._call(url=PRODUCT_REGISTER_URL, sub_url=PRODUCT_REGISTER_SUB_URL, post=True,
                             json={'id': prod_id, 'name': name, 'description': desc})

        if r.status_code == 201:
            return

        self._invalid_response(sub_url=PRODUCT_OFFERS_SUB_URL, expected_codes=(400, 401), r=r, json=json)

    def product_offers(self, prod_id: int) -> List[Dict]:
        r, json = self._call(url=PRODUCT_OFFERS_URL.format(prod_id=prod_id), sub_url=PRODUCT_OFFERS_SUB_URL)

        if r.status_code == 200:
            return list(json)

        self._invalid_response(sub_url=PRODUCT_OFFERS_SUB_URL, expected_codes=(400, 401, 404), r=r, json=json)

    # PRIVATE METHODS

    def _call(self, url: str, sub_url: str, post: bool = False, json: Dict = None) -> Tuple[requests.Response, Dict]:
        if self.access_token is None and sub_url != AUTH_SUB_URL:
            raise OffersConnector.ENoAuth(url=sub_url)

        try:
            headers = {'Bearer': self.access_token}
            if post:
                r = requests.post(url, headers=headers, json=json)
            else:
                r = requests.get(url, headers=headers)
        except Exception as e:
            raise OffersConnector.ERequestException(url=sub_url, original_exception=e)

        try:
            json = r.json()
        except Exception as e:
            raise OffersConnector.EInvalidJSONResponse(
                url=url,
                code=r.status_code,
                raw_response=r.text,
                original_exception=e
            )

        return r, json

    @staticmethod
    def _invalid_response(sub_url: str, expected_codes: Tuple[int, ...], r: requests.Response, json: dict) -> None:
        response_valid = (ERROR_MESSAGE in json) and (ERROR_CODE in json)
        if (r.status_code in expected_codes) and response_valid:
            raise OffersConnector.EExpectedErrorResponse.make_descendant(
                url=sub_url, code=json[ERROR_CODE], msg=json[ERROR_MESSAGE])

        raise OffersConnector.EUnexpectedResponse(url=sub_url, code=r.status_code, json=json)

