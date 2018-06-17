"""
GitHub OAuth Views
"""

from django.contrib.auth import get_user_model
from supervisr.core.models import make_username
from supervisr.mod.auth.oauth.client.errors import OAuthClientEmailMissingError
from supervisr.mod.auth.oauth.client.utils import user_get_or_create
from supervisr.mod.auth.oauth.client.views.core import OAuthCallback


class GitHubOAuth2Callback(OAuthCallback):
    """
    GitHub OAuth2 Callback
    """

    def get_or_create_user(self, provider, access, info):
        if 'email' not in info or info['email'] == '':
            raise OAuthClientEmailMissingError()
        user = get_user_model()
        user_data = {
            user.USERNAME_FIELD: info.get('login'),
            'email': info.get('email', ''),
            'first_name': info.get('name'),
            'password': None,
            'crypt6_password': '',  # Set password to empty to disable login
            'unix_username': make_username(info.get('login')),
        }
        gh_user = user_get_or_create(user_model=user, **user_data)
        return gh_user
