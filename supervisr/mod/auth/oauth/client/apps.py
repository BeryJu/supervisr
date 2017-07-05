"""
Supervisr auth oauth client app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthOAuthClientAppConfig(SupervisrAppConfig):
    """
    Supervisr auth oauth client app config
    """

    name = 'supervisr.mod.auth.oauth.client'
    title_moddifier = lambda self, title, request: 'OAuth/Client'
    label = 'supervisr/mod/auth/oauth/client'
    view_user_settings = 'user_settings'
