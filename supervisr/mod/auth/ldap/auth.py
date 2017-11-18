"""supervisr mod ldap Authentication Backend"""

from django.contrib.auth.backends import ModelBackend

from supervisr.mod.auth.ldap.ldap_connector import LDAPConnector


class LDAPBackend(ModelBackend):
    """Authenticate users against LDAP Server"""

    _ldap = None

    def __init__(self, *args, **kwargs):
        super(LDAPBackend, self).__init__(*args, **kwargs)
        self._ldap = LDAPConnector()

    # def user_can_authenticate(self, user):
    #     """Check if user is disabled in LDAP"""
    #     pass

    def authenticate(self, **kwargs):
        """Try to authenticate a user via ldap"""
        password = kwargs.pop('password')
        return self._ldap.auth_user(password, **kwargs)
