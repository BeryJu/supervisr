"""
Supervisr OAuth2 Views
"""

import json
import logging

from django.contrib.auth import get_user_model
from requests.exceptions import RequestException

from supervisr.core.models import make_username
from supervisr.mod.auth.oauth.client.clients import OAuth2Client
from supervisr.mod.auth.oauth.client.utils import user_get_or_create
from supervisr.mod.auth.oauth.client.views.core import OAuthCallback

LOGGER = logging.getLogger(__name__)

class SupervisrOAuth2Client(OAuth2Client):
    """
    Supervisr OAuth2 Client
    """

    def get_profile_info(self, raw_token):
        "Fetch user profile information."
        try:
            token = json.loads(raw_token)['access_token']
            headers = {
                'Authorization': 'Bearer:%s' % token
            }
            response = self.request('get', self.provider.profile_url,
                                    token=raw_token, headers=headers)
            response.raise_for_status()
        except RequestException as exc:
            LOGGER.warning('Unable to fetch user profile: %s', exc)
            return None
        else:
            return response.json() or response.text

class SupervisrOAuthCallback(OAuthCallback):
    """
    Supervisr OAuth2 Callback
    """

    client_class = SupervisrOAuth2Client

    def get_user_id(self, provider, info):
        return info['pk']

    def get_or_create_user(self, provider, access, info):
        user = get_user_model()
        user_data = {
            user.USERNAME_FIELD: info['username'],
            'email': info['email'],
            'first_name': info['first_name'],
            'password': None,
            'crypt6_password': '',  # Set password to empty to disable login
            'unix_username': make_username(info['first_name'])
        }
        sv_user = user_get_or_create(user_model=user, **user_data)
        return sv_user
