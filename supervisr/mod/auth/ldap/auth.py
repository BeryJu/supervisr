"""supervisr mod ldap Authentication Backend"""

from django.contrib.auth.backends import ModelBackend

from supervisr.mod.auth.ldap.ldap_connector import LDAPConnector


class LDAPBackend(ModelBackend):
    """Authenticate users against LDAP Server"""

    _ldap = None

    def __init__(self, *args, **kwargs):
        super(LDAPBackend, self).__init__(*args, **kwargs)
        self._ldap = LDAPConnector()

    def authenticate(self, **kwargs):
        """Try to authenticate a user via ldap"""
        if 'password' not in kwargs:
            return None
        return self._ldap.auth_user(**kwargs)
