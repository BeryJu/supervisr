"""
Supervisr mod_ldap app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthLDAPConfig(SupervisrAppConfig):
    """
    Supervisr mod_ldap app config
    """

    name = 'supervisr.mod.auth.ldap'
    label = 'supervisr/mod/auth/ldap'
    title_moddifier = lambda self, title, request: 'LDAP'
    admin_url_name = 'supervisr/mod/auth/ldap:admin_settings'

    def ensure_settings(self):
        return {
            'enabled': False,
            'server': '',
            'base': '',
            'create_base': '',
            'bind:user': '',
            'bind:password': '',
            'domain': '',
        }
