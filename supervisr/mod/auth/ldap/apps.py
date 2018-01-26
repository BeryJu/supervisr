"""Supervisr mod_ldap app config"""

from supervisr.core.apps import SupervisrAppConfig


class SupervisrModAuthLDAPConfig(SupervisrAppConfig):
    """Supervisr mod_ldap app config"""

    name = 'supervisr.mod.auth.ldap'
    label = 'supervisr_mod_auth_ldap'
    title_modifier = lambda self, request: 'LDAP'
    admin_url_name = 'supervisr_mod_auth_ldap:admin_settings'
    verbose_name = 'Supervisr mod_auth_ldap'

    def ensure_settings(self):
        return {
            'enabled': False,
            'mode': 0,
            'server': '',
            'server:tls': False,
            'base': '',
            'create_base': '',
            'bind:user': '',
            'bind:password': '',
            'domain': '',
        }
