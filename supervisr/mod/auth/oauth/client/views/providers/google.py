"""
Google OAuth Views
"""
from django.contrib.auth import get_user_model

from supervisr.core.models import make_username
from supervisr.mod.auth.oauth.client.utils import user_get_or_create
from supervisr.mod.auth.oauth.client.views.core import (OAuthCallback,
                                                        OAuthRedirect)


class GoogleOAuthRedirect(OAuthRedirect):
    """
    Google OAuth2 Redirect
    """

    def get_additional_parameters(self, provider):
        return {
            'scope': 'email profile',
        }


class GoogleOAuth2Callback(OAuthCallback):
    """
    Google OAuth2 Callback
    """

    def get_or_create_user(self, provider, access, info):
        user = get_user_model()
        user_data = {
            user.USERNAME_FIELD: info.get('email'),
            'email': info.get('email', ''),
            'first_name': info.get('name'),
            'password': None,
            'crypt6_password': '',  # Set password to empty to disable login
            'unix_username': make_username(info.get('id'))
        }
        google_user = user_get_or_create(user_model=user, **user_data)
        return google_user
