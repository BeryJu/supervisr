"""
Supervisr mod_ldap app config
"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthLDAPConfig(SupervisrAppConfig):
    """
    Supervisr mod_ldap app config
    """

    name = 'supervisr.mod.auth.ldap'
    title_moddifier = lambda self, title, request: title.upper()
    admin_url_name = 'ldap:admin_settings'

    def ensure_settings(self):
        return {
            'mod:ldap:enabled': False,
            'mod:ldap:server': '',
            'mod:ldap:base': '',
            'mod:ldap:create_base': '',
            'mod:ldap:bind:user': '',
            'mod:ldap:bind:password': '',
            'mod:ldap:domain': '',
        }
