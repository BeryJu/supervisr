"""
Supervisr mod_ldap app config
"""

from supervisr.apps import SupervisrAppConfig


class SupervisrModLDAPConfig(SupervisrAppConfig):
    """
    Supervisr mod_ldap app config
    """

    name = 'supervisr_mod_ldap'

    def ready(self):
        super(SupervisrModLDAPConfig, self).ready()
