"""
Wrapper for ldap3 to easily manage user
"""
import logging
import os
import sys
import time

from ldap3 import (MOCK_SYNC, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE,
                   OFFLINE_AD_2012_R2, Connection, Server)
from ldap3.core.exceptions import LDAPException, LDAPInvalidCredentialsResult

from supervisr.models import Setting

LOGGER = logging.getLogger(__name__)

class LDAPConnector(object):
    """
    Wrapper for ldap3 to easily manage user
    """

    con = None
    domain = None
    base_dn = None
    mock = False

    def __init__(self, mock=False):
        super(LDAPConnector, self).__init__()
        if LDAPConnector.enabled() is False:
            LOGGER.warning("LDAP not Enabled")
            return
        # Either use mock argument or test is in argv
        if mock is False and 'test' not in sys.argv:
            self.domain = Setting.get('supervisr:ldap:domain')
            self.base_dn = Setting.get('supervisr:ldap:base')
            full_user = Setting.get('supervisr:ldap:bind:user')+'@'+self.domain
            self.server = Server(Setting.get('supervisr:ldap:server'))
            self.con = Connection(self.server, raise_exceptions=True,
                                  user=full_user,
                                  password=Setting.get('supervisr:ldap:bind:password'))
            self.con.bind()
            self.con.start_tls()
        else:
            self.mock = True
            self.domain = 'mock.beryju.org'
            self.base_dn = 'OU=customers,DC=mock,DC=beryju,DC=org'
            self.server = Server('dc1.mock.beryju.org', get_info=OFFLINE_AD_2012_R2)
            self.con = Connection(self.server, raise_exceptions=True,
                                  user='CN=mockadm,OU=customers,DC=mock,DC=beryju,DC=org',
                                  password='b3ryju0rg!', client_strategy=MOCK_SYNC)
            json_path = os.path.join(os.path.dirname(__file__), 'test', 'ldap_mock.json')
            self.con.strategy.entries_from_json(json_path)
            self.con.bind()

    # Switch so we can easily disable LDAP
    @staticmethod
    def enabled():
        """
        Returns whether LDAP is enabled or not
        """
        return Setting.objects.get(key='supervisr:ldap:enabled').value_bool or \
            'test' in sys.argv

    @staticmethod
    def get_server():
        """
        Return the saved LDAP Server
        """
        return Setting.objects.get(key='supervisr:ldap:server')

    @staticmethod
    def encode_pass(password):
        """
        Encodes a plain-text password so it can be used by AD
        """
        return '"{}"'.format(password).encode('utf-16-le')

    def mail_to_dn(self, mail):
        """
        Search email in LDAP and return the DN.
        Returns False if nothing was found.
        """
        # Find out dn for user
        ldap_filter = "(mail=%s)" % mail
        self.con.search(self.base_dn, ldap_filter)
        results = self.con.response
        if len(results) == 1:
            return str(results[0]['dn'])
        else:
            return False

    def auth_user(self, password, user_dn=None, mail=None):
        """
        Try to bind as either user_dn or mail with password.
        Returns True on success, otherwise False
        """
        if user_dn is None and mail is None:
            return False
        if user_dn is None:
            user_dn = self.mail_to_dn(mail)
        # Try to bind as new user
        LOGGER.debug("binding as '%s'", user_dn)
        try:
            t_con = Connection(self.server, user=user_dn, password=password, raise_exceptions=True)
            t_con.bind()
            return True
        except LDAPInvalidCredentialsResult as exception:
            LOGGER.debug("User '%s' failed to login (Wrong credentials)", user_dn)
        except LDAPException as exception:
            LOGGER.error(exception)
        return False

    def is_email_used(self, mail):
        """
        Checks whether an email address is already registered in LDAP
        """
        ldap_filter = "(mail=%s)" % mail
        return self.con.search(self.base_dn, ldap_filter)

    def create_user(self, user, raw_password):
        """
        Creates a new LDAP User from a django user and raw_password.
        Returns True on success, otherwise False
        """
        # The dn of our new entry/object
        username = 'c_' + str(user.id) + '_' + user.username
        # sAMAccountName is limited to 20 chars
        # https://msdn.microsoft.com/en-us/library/ms679635.aspx
        username_trunk = username[:20] if len(username) > 20 else username
        user_dn = 'cn='+username+','+self.base_dn
        LOGGER.info('New DN: '+user_dn)
        attrs = {
            'distinguishedName' : str(user_dn),
            'cn'                : str(username),
            'description'       : str('t='+str(time.time())),
            'sAMAccountName'    : str(username_trunk),
            'givenName'         : str(user.username),
            'displayName'       : str(user.first_name),
            'mail'              : str(user.email),
            'userPrincipalName' : str(username+'@'+self.domain),
            'objectclass'       : ['top', 'person', 'organizationalPerson', 'user'],
        }
        try:
            self.con.add(user_dn, 'user', attrs)
        except LDAPException as exception:
            LOGGER.error("Failed to create user ('%s')", exception)
            return False
        return self.change_password(raw_password, mail=user.email)

    def disable_user(self, mail=None, user_dn=None):
        """
        Disables LDAP user based on mail or user_dn.
        Returns True on success, otherwise False
        """
        if mail is None and user_dn is None:
            return False
        if user_dn is None and mail is not None:
            user_dn = self.mail_to_dn(mail)
        self.con.modify(user_dn, {
            'userAccountControl': [(MODIFY_REPLACE, [str(66050)])],
        })
        LOGGER.debug("disabled account '%s'", user_dn)
        return 'result' in self.con.result and self.con.result['result'] == 0

    def enable_user(self, mail=None, user_dn=None):
        """
        Enables LDAP user based on mail or user_dn.
        Returns True on success, otherwise False
        """
        if mail is None and user_dn is None:
            return False
        if user_dn is None and mail is not None:
            user_dn = self.mail_to_dn(mail)
        self.con.modify(user_dn, {
            'userAccountControl': [(MODIFY_REPLACE, [str(66048)])],
        })
        LOGGER.debug("enabled account '%s'", user_dn)
        return 'result' in self.con.result and self.con.result['result'] == 0

    def change_password(self, new_password, mail=None, user_dn=None):
        """
        Changes LDAP user's password based on mail or user_dn.
        Returns True on success, otherwise False
        """
        if mail is None and user_dn is None:
            return False
        if user_dn is None and mail is not None:
            user_dn = self.mail_to_dn(mail)
        self.con.modify(user_dn, {
            'unicodePwd': [(MODIFY_REPLACE, [LDAPConnector.encode_pass(new_password)])],
        })
        self.enable_user(user_dn=user_dn)
        LOGGER.debug("changed password for '%s'", user_dn)
        return 'result' in self.con.result and self.con.result['result'] == 0

    def add_to_group(self, group_dn, mail=None, user_dn=None):
        """
        Adds mail or user_dn to group_dn
        Returns True on success, otherwise False
        """
        if mail is None and user_dn is None:
            return False
        if user_dn is None and mail is not None:
            user_dn = self.mail_to_dn(mail)
        self.con.modify(group_dn, {
            'member': [(MODIFY_ADD), [user_dn]]
        })
        LOGGER.debug("added %s to group %s", user_dn, group_dn)
        return 'result' in self.con.result and self.con.result['result'] == 0

    def remove_from_group(self, group_dn, mail=None, user_dn=None):
        """
        Removes mail or user_dn from group_dn
        Returns True on success, otherwise False
        """
        if mail is None and user_dn is None:
            return False
        if user_dn is None and mail is not None:
            user_dn = self.mail_to_dn(mail)
        self.con.modify(group_dn, {
            'member': [(MODIFY_DELETE), [user_dn]]
        })
        LOGGER.debug("removed %s from group %s", user_dn, group_dn)
        return 'result' in self.con.result and self.con.result['result'] == 0
