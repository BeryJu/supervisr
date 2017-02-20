"""
Supervisr mod_ldap app config
"""

from supervisr.apps import SupervisrAppConfig


class SupervisrModLdapConfig(SupervisrAppConfig):
    """
    Supervisr mod_ldap app config
    """

    name = 'supervisr_mod_ldap'

    def ready(self):
        super(SupervisrModLdapConfig, self).ready()
