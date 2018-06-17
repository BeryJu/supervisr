"""
Twitter OAuth Views
"""

import logging

from django.contrib.auth import get_user_model
from requests.exceptions import RequestException
from supervisr.core.models import make_username
from supervisr.mod.auth.oauth.client.clients import OAuthClient
from supervisr.mod.auth.oauth.client.errors import OAuthClientEmailMissingError
from supervisr.mod.auth.oauth.client.utils import user_get_or_create
from supervisr.mod.auth.oauth.client.views.core import OAuthCallback

LOGGER = logging.getLogger(__name__)


class TwitterOAuthClient(OAuthClient):
    """
    Twitter OAuth2 Client
    """

    def get_profile_info(self, raw_token):
        "Fetch user profile information."
        try:
            response = self.request('get', self.provider.profile_url + "?include_email=true",
                                    token=raw_token)
            response.raise_for_status()
        except RequestException as exc:
            LOGGER.warning('Unable to fetch user profile: %s', exc)
            return None
        else:
            return response.json() or response.text


class TwitterOAuthCallback(OAuthCallback):
    """
    Twitter OAuth2 Callback
    """

    client_class = TwitterOAuthClient

    def get_or_create_user(self, provider, access, info):
        if 'email' not in info:
            raise OAuthClientEmailMissingError()
        user = get_user_model()
        user_data = {
            user.USERNAME_FIELD: info.get('screen_name'),
            'email': info.get('email', ''),
            'first_name': info.get('name'),
            'password': None,
            'crypt6_password': '',  # Set password to empty to disable login
            'unix_username': make_username(info.get('screen_name'))
        }
        tw_user = user_get_or_create(user_model=user, **user_data)
        return tw_user
