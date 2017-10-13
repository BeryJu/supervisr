"""
Supervisr auth oauth provider app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthOAuthProviderConfig(SupervisrAppConfig):
    """
    Supervisr auth oauth provider app config
    """

    name = 'supervisr.mod.auth.oauth.provider'
    title_moddifier = lambda self, title, request: 'OAuth/Provider'
