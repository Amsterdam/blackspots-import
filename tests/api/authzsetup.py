import time

from authorization_django.jwks import get_keyset
from django.conf import settings
from jwcrypto.jwt import JWT
from rest_framework.test import APIClient


class AuthorizationSetup(object):
    """
    Helper methods to setup JWT tokens and authorization levels

    sets the following attributes:

    auth_token_read
    auth_token_read_write
    """
    anon_client = None
    read_client = None
    write_client = None

    def setup_clients(self):
        # use the DRF api client. See why:
        # https://www.django-rest-framework.org/api-guide/testing/#put-and-patch-with-form-data
        self.anon_client = APIClient()

        token_read = self._get_token(settings.SCOPE_BS_READ)
        self.read_client = APIClient()
        self.read_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token_read))

        token_read_write = self._get_token(settings.SCOPE_BS_WRITE)
        self.write_client = APIClient()
        self.write_client.credentials(HTTP_AUTHORIZATION='Bearer {}'.format(token_read_write))

    def _get_token(self, scope):
        """
        Obtain a token to be used in the http client:

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(token))

        """
        jwks = get_keyset()
        assert len(jwks["keys"]) > 0

        key = next(iter(jwks["keys"]))
        now = int(time.time())

        header = {"alg": "ES256", "kid": key.key_id}  # algorithm of the test key

        token = JWT(
            header=header,
            claims={
                "iat": now,
                "exp": now + 600,
                "scopes": [scope],
            },
        )
        token.make_signed_token(key)
        return token.serialize()
