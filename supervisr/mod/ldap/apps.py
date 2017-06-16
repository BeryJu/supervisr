"""
Supervisr mod_ldap app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModLDAPConfig(SupervisrAppConfig):
    """
    Supervisr mod_ldap app config
    """

    name = 'supervisr.mod.ldap'
    title_moddifier = lambda self, title, request: title.upper()
    admin_url_name = 'ldap:admin_settings'
