"""
Wrapper for ldap3 to easily manage user
"""
import logging
import os
import sys
import time as py_time

from ldap3 import (MOCK_SYNC, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE,
                   OFFLINE_AD_2012_R2, Connection, Server)
from ldap3.core.exceptions import LDAPException, LDAPInvalidCredentialsResult

from supervisr.core.models import Setting
from supervisr.core.utils import send_admin_mail, time
from supervisr.mod.auth.ldap.errors import LDAPUserNotFound
from supervisr.mod.auth.ldap.models import LDAPModification

LOGGER = logging.getLogger(__name__)

class LDAPConnector(object):
    """
    Wrapper for ldap3 to easily manage user
    """

    con = None
    domain = None
    base_dn = None
    mock = False

    @time(statistic_key='ldap.ldap_connector.init')
    def __init__(self, mock=False):
        super(LDAPConnector, self).__init__()
        if LDAPConnector.enabled() is False:
            LOGGER.warning("LDAP not Enabled")
            return
        # Either use mock argument or test is in argv
        if mock is False and 'test' not in sys.argv:
            self.domain = Setting.get('domain')
            self.base_dn = Setting.get('base')
            full_user = Setting.get('bind:user')+'@'+self.domain
            self.server = Server(Setting.get('server'))
            self.con = Connection(self.server, raise_exceptions=True,
                                  user=full_user,
                                  password=Setting.get('bind:password'))
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
        # Apply LDAPModification's from DB
        # self.apply_db()

    @staticmethod
    def cleanup_mock():
        """
        Cleanup mock files which are not this PID's
        """
        pid = os.getpid()
        json_path = os.path.join(os.path.dirname(__file__), 'test', 'ldap_mock_%d.json' % pid)
        os.unlink(json_path)
        LOGGER.info("Cleaned up LDAP Mock from PID %d", pid)

    def __del__(self):
        """
        Write entries to json
        """
        # pid = os.getpid()
        # json_path = os.path.join(os.path.dirname(__file__), 'test', 'ldap_mock_%d.json' % pid)
        # if self.con.search(self.base_dn, '(objectclass=*)', attributes=ALL_ATTRIBUTES):
        #     self.con.response_to_file(json_path, raw=True)
        # LOGGER.info("Saved LDAP State as %s" % json_path)

    def apply_db(self):
        """
        Check if any unapplied LDAPModification's are left
        """
        to_apply = LDAPModification.objects.filter(_purgeable=False)
        for obj in to_apply:
            try:
                if obj.action == LDAPModification.ACTION_ADD:
                    self.con.add(obj.dn, obj.data)
                elif obj.action == LDAPModification.ACTION_MODIFY:
                    self.con.modify(obj.dn, obj.data)

                # Object has been successfully applied to LDAP
                obj.delete()
            except LDAPException as exc:
                send_admin_mail(exc, """
                    Failed to apply LDAPModification#%s
                    """ % obj.ldap_moddification_id)
        LOGGER.info("Recovered %s Modifications from DB.", len(to_apply))

    @staticmethod
    def handle_ldap_error(object_dn, action, data):
        """
        Custom Handler for LDAP methods to write LDIF to DB
        """
        LDAPModification.objects.create(
            dn=object_dn,
            action=action,
            data=data)

    # Switch so we can easily disable LDAP
    @staticmethod
    def enabled():
        """
        Returns whether LDAP is enabled or not
        """
        return Setting.get(key='enabled') == 'True' or 'test' in sys.argv

    @staticmethod
    def get_server():
        """
        Return the saved LDAP Server
        """
        return Setting.get(key='server')

    @staticmethod
    def encode_pass(password):
        """
        Encodes a plain-text password so it can be used by AD
        """
        return '"{}"'.format(password).encode('utf-16-le')

    @time(statistic_key='ldap.ldap_connector.mail_to_dn')
    def mail_to_dn(self, mail):
        """
        Search email in LDAP and return the DN.
        Returns False if nothing was found.
        """
        # Find out dn for user
        ldap_filter = "(mail=%s)" % mail
        self.con.search(self.base_dn, ldap_filter)
        results = self.con.response

        if len(results) >= 1:
            return str(results[0]['dn'])
        else:
            raise LDAPUserNotFound("User '%s' not found" % mail)

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
            LOGGER.warning(exception)
        return False

    def is_email_used(self, mail):
        """
        Checks whether an email address is already registered in LDAP
        """
        ldap_filter = "(mail=%s)" % mail
        return self.con.search(self.base_dn, ldap_filter)

    @time(statistic_key='ldap.ldap_connector.create_user')
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
        # AD doesn't like sAMAccountName's with . at the end
        username_trunk = username_trunk[:-1] if username_trunk[-1] == '.' else username_trunk
        user_dn = 'cn='+username+','+self.base_dn
        LOGGER.info('New DN: '+user_dn)
        attrs = {
            'distinguishedName' : str(user_dn),
            'cn'                : str(username),
            'description'       : str('t='+str(py_time.time())),
            'sAMAccountName'    : str(username_trunk),
            'givenName'         : str(user.first_name),
            'displayName'       : str(user.first_name),
            'name'              : str(user.first_name),
            'mail'              : str(user.email),
            'userPrincipalName' : str(username+'@'+self.domain),
            'objectClass'       : ['top', 'person', 'organizationalPerson', 'user'],
        }
        try:
            self.con.add(user_dn, attributes=attrs)
        except LDAPException as exception:
            LOGGER.warning("Failed to create user ('%s'), saved to DB", exception)
            LDAPConnector.handle_ldap_error(user_dn, LDAPModification.ACTION_ADD, attrs)
        LOGGER.info("Signed up user %s", user.email)
        return self.change_password(raw_password, mail=user.email)

    @time(statistic_key='ldap.ldap_connector._do_modify')
    def _do_modify(self, diff, mail=None, user_dn=None):
        """
        Do the LDAP modification itself
        """
        if mail is None and user_dn is None:
            return False
        if user_dn is None and mail is not None:
            user_dn = self.mail_to_dn(mail)

        try:
            self.con.modify(user_dn, diff)
        except LDAPException as exception:
            LOGGER.warning("Failed to modify %s ('%s'), saved to DB", user_dn, exception)
            LDAPConnector.handle_ldap_error(user_dn, LDAPModification.ACTION_MODIFY, diff)
        LOGGER.debug("moddified account '%s' [%s]", user_dn, ','.join(diff.keys()))
        return 'result' in self.con.result and self.con.result['result'] == 0

    def disable_user(self, mail=None, user_dn=None):
        """
        Disables LDAP user based on mail or user_dn.
        Returns True on success, otherwise False
        """
        diff = {
            'userAccountControl': [(MODIFY_REPLACE, [str(66050)])],
        }
        return self._do_modify(diff, mail=mail, user_dn=user_dn)

    def enable_user(self, mail=None, user_dn=None):
        """
        Enables LDAP user based on mail or user_dn.
        Returns True on success, otherwise False
        """
        diff = {
            'userAccountControl': [(MODIFY_REPLACE, [str(66048)])],
        }
        return self._do_modify(diff, mail=mail, user_dn=user_dn)

    def change_password(self, new_password, mail=None, user_dn=None):
        """
        Changes LDAP user's password based on mail or user_dn.
        Returns True on success, otherwise False
        """
        diff = {
            'unicodePwd': [(MODIFY_REPLACE, [LDAPConnector.encode_pass(new_password)])],
        }
        return self._do_modify(diff, mail=mail, user_dn=user_dn)

    def add_to_group(self, group_dn, mail=None, user_dn=None):
        """
        Adds mail or user_dn to group_dn
        Returns True on success, otherwise False
        """
        if mail is None and user_dn is None:
            return False
        if user_dn is None and mail is not None:
            user_dn = self.mail_to_dn(mail)
        diff = {
            'member': [(MODIFY_ADD), [user_dn]]
        }
        return self._do_modify(diff, user_dn=group_dn)

    def remove_from_group(self, group_dn, mail=None, user_dn=None):
        """
        Removes mail or user_dn from group_dn
        Returns True on success, otherwise False
        """
        if mail is None and user_dn is None:
            return False
        if user_dn is None and mail is not None:
            user_dn = self.mail_to_dn(mail)
        diff = {
            'member': [(MODIFY_DELETE), [user_dn]]
        }
        return self._do_modify(diff, user_dn=group_dn)
