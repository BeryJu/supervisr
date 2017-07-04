"""
Supervisr OAuth2 Views
"""

import json
import logging

from allaccess.clients import OAuth2Client
from allaccess.views import OAuthCallback
from django.contrib.auth import get_user_model
from requests.exceptions import RequestException

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
            LOGGER.error('Unable to fetch user profile: %s', exc)
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
        kwargs = {
            user.USERNAME_FIELD: info['email'],
            'email': info['email'],
            'first_name': info['first_name'],
            'password': None
        }
        return user.objects.create_user(**kwargs)
