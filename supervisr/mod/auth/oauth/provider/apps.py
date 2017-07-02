"""
Supervisr mod_ldap app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthOAuthProviderAppConfig(SupervisrAppConfig):
    """
    Supervisr mod_ldap app config
    """

    name = 'supervisr.mod.auth.oauth.provider'
    title_moddifier = lambda self, title, request: 'OAuth/Provider'
