"""Reddit OAuth Views"""
import json
import logging

from django.contrib.auth import get_user_model
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from supervisr.core.models import make_username
from supervisr.mod.auth.oauth.client.clients import OAuth2Client
from supervisr.mod.auth.oauth.client.utils import user_get_or_create
from supervisr.mod.auth.oauth.client.views.core import (OAuthCallback,
                                                        OAuthRedirect)

LOGGER = logging.getLogger(__name__)


class RedditOAuthRedirect(OAuthRedirect):
    """Reddit OAuth2 Redirect"""

    def get_additional_parameters(self, provider):
        return {
            'scope': 'identity',
            'duration': 'permanent',
        }


class RedditOAuth2Client(OAuth2Client):
    """Reddit OAuth2 Client"""

    def get_access_token(self, request, callback=None, **request_kwargs):
        "Fetch access token from callback request."
        auth = HTTPBasicAuth(
            self.provider.consumer_key,
            self.provider.consumer_secret)
        return super(RedditOAuth2Client, self).get_access_token(request, callback, auth=auth)

    def get_profile_info(self, raw_token):
        "Fetch user profile information."
        try:
            token = json.loads(raw_token)
            headers = {
                'Authorization': '%s %s' % (token['token_type'], token['access_token'])
            }
            response = self.request('get', self.provider.profile_url,
                                    token=token['access_token'], headers=headers)
            response.raise_for_status()
        except RequestException as exc:
            LOGGER.warning('Unable to fetch user profile: %s', exc)
            return None
        else:
            return response.json() or response.text


class RedditOAuth2Callback(OAuthCallback):
    """Reddit OAuth2 Callback"""

    client_class = RedditOAuth2Client

    def get_or_create_user(self, provider, access, info):
        user = get_user_model()
        user_data = {
            user.USERNAME_FIELD: info.get('name'),
            'email': None,
            'first_name': info.get('name'),
            'password': None,
            'crypt6_password': '',  # Set password to empty to disable login
            'unix_username': make_username(info.get('name'))
        }
        reddit_user = user_get_or_create(user_model=user, **user_data)
        return reddit_user
