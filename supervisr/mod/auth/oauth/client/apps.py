"""Supervisr auth oauth client app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthOAuthClientConfig(SupervisrAppConfig):
    """Supervisr auth oauth client app config"""

    name = 'supervisr.mod.auth.oauth.client'
    title_modifier = lambda self, request: 'OAuth/Client'
    label = 'supervisr_mod_auth_oauth_client'
    view_user_settings = 'user_settings'
    verbose_name = 'Supervisr mod_auth_oauth_client'
