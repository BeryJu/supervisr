"""
Supervisr auth oauth client app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthOAuthClientConfig(SupervisrAppConfig):
    """
    Supervisr auth oauth client app config
    """

    name = 'supervisr.mod.auth.oauth.client'
    title_modifier = lambda self, title, request: 'OAuth/Client'
    label = 'supervisr/mod/auth/oauth/client'
    view_user_settings = 'user_settings'
    verbose_name = 'Supervisr mod/auth/oauth/client'
