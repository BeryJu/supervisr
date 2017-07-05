"""
GitHub OAuth Views
"""

from django.contrib.auth import get_user_model

from supervisr.core.models import UserProfile, make_username
from supervisr.mod.auth.oauth.client.views.core import OAuthCallback


class GitHubOAuth2Callback(OAuthCallback):
    """
    GitHub OAuth2 Callback
    """

    def get_or_create_user(self, provider, access, info):
        user = get_user_model()
        user_data = {
            user.USERNAME_FIELD: info['email'],
            'email': info['email'],
            'first_name': info['name'],
            'password': None
        }
        gh_user = user.objects.create_user(**user_data)
        UserProfile.objects.get_or_create(
            user=gh_user,
            defaults={
                'username': info['login'],
                'crypt6_password': '', # Set password to empty to disable login
                'unix_username': make_username(info['login'])
            })
        return gh_user
