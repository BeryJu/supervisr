import logging
import os
import sys
import time

from ldap3 import (ALL, ALL_ATTRIBUTES, MOCK_SYNC, MODIFY_REPLACE,
                   OFFLINE_AD_2012_R2, Connection, Server)
from ldap3.core.exceptions import (LDAPInvalidCredentialsResult,
                                   LDAPOperationResult)
from ldap3.extend.microsoft.modifyPassword import modify_ad_password
from ldap3.extend.microsoft.unlockAccount import unlock_ad_account

from .models import Setting

logger = logging.getLogger(__name__)

class LDAPConnector(object):

    con = None
    domain = None
    base_dn = None
    mock = False

    def __init__(self, mock=False):
        super(LDAPConnector, self).__init__()
        if LDAPConnector.enabled() is False:
            logger.warning("LDAP not Enabled")
            return
        # Either use mock argument or test is in argv
        if mock is False and 'test' not in sys.argv:
            self.domain = Setting.get('supervisr:ldap:domain')
            self.base_dn = Setting.get('supervisr:ldap:base')
            full_user = Setting.get('supervisr:ldap:bind:user')+'@'+self.domain
            self.server = Server(Setting.get('supervisr:ldap:server'))
            self.con = Connection(self.server, raise_exceptions=True,
                user=full_user, password=Setting.get('supervisr:ldap:bind:password'))
            self.con.bind()
            self.con.start_tls()
        else:
            self.mock = True
            self.domain = 'mock.beryju.org'
            self.base_dn = 'OU=customers,DC=mock,DC=beryju,DC=org'
            self.server = Server('dc1.mock.beryju.org', get_info=OFFLINE_AD_2012_R2)
            self.con = Connection(self.server, raise_exceptions=True,
                user='CN=mockadm,OU=customers,DC=mock,DC=beryju,DC=org', password='b3ryju0rg!',
                client_strategy=MOCK_SYNC)
            json_path = os.path.join(os.path.dirname(__file__), 'test', 'ldap_mock.json')
            self.con.strategy.entries_from_json(json_path)
            self.con.bind()

    # Switch so we can easily disable LDAP
    @staticmethod
    def enabled():
        return Setting.objects.get(key='supervisr:ldap:enabled').value_bool or \
            'test' in sys.argv

    @staticmethod
    def encode_pass(password):
        return '"{}"'.format(password).encode('utf-16-le')

    def mail_to_dn(self, mail):
        # Find out dn for user
        filter = "(mail=%s)" % mail
        try:
            assert self.con.search(self.base_dn, filter) == True
        except Exception as e:
            logger.error(filter)
        results = self.con.response
        assert len(results) == 1
        return str(results[0]['dn'])

    def auth_user(self, mail, password):
        upn = self.mail_to_dn(mail, field='userPrincipalName')
        # Try to bind as new user
        logger.debug("binding as '%s'" % upn)
        try:
            t_con = Connection(self.server, user=upn, password=password, raise_exceptions=True)
            t_con.bind()
            return True
        except LDAPInvalidCredentialsResult as e:
            logger.debug("User '%s' failed to login (Wrong credentials)" % upn)
        except Exception as e:
            logger.error(e)
        return False

    def is_email_used(self, mail):
        filter = "(mail=%s)" % mail
        return self.con.search(self.base_dn, filter)

    def create_user(self, user, raw_password):
        # The dn of our new entry/object
        username = 'c_' + str(user.id) + '_' + user.username
        # sAMAccountName is limited to 20 chars (https://msdn.microsoft.com/en-us/library/ms679635.aspx)
        username_trunk = username[:20] if len(username) > 20 else username
        dn = 'cn='+username+','+self.base_dn
        logger.info('New DN: '+dn)
        attrs = {
            'distinguishedName' : str(dn),
            'cn'                : str(username),
            'description'       : str('t='+str(time.time())),
            'sAMAccountName'    : str(username_trunk),
            'givenName'         : str(user.username),
            'displayName'       : str(user.first_name),
            'mail'              : str(user.email),
            'userPrincipalName' : str(username+'@'+self.domain),
            'objectclass'       : ['top','person','organizationalPerson', 'user'],
        }
        try:
            self.con.add(dn, 'user', attrs)
        except LDAPOperationResult as e:
            logger.error("Failed to create user ('%s')" % e)
            return False
        except Exception as e:
            logger.error(e)
            return False
        return self.change_password(raw_password, mail=user.email)

    def disable_user(self, mail=None, dn=None):
        if mail is None and dn is None:
            return False
        if dn is None and mail is not None:
            dn = self.mail_to_dn(mail)
        self.con.modify(dn, {
            'userAccountControl': [(MODIFY_REPLACE, [str(66050)])],
        })
        logger.debug("disabled account '%s'" % dn)
        return 'result' in self.con.result and self.con.result['result'] == 0

    def enable_user(self, mail=None, dn=None):
        if mail is None and dn is None:
            return False
        if dn is None and mail is not None:
            dn = self.mail_to_dn(mail)
        self.con.modify(dn, {
            'userAccountControl': [(MODIFY_REPLACE, [str(66048)])],
        })
        logger.debug("enabled account '%s'" % dn)
        return 'result' in self.con.result and self.con.result['result'] == 0

    def change_password(self, new_password, mail=None, dn=None):
        if mail is None and dn is None:
            return False
        if dn is None and mail is not None:
            dn = self.mail_to_dn(mail)
        self.con.modify(dn, {
            'unicodePwd': [(MODIFY_REPLACE, [LDAPConnector.encode_pass(new_password)])],
        })
        self.enable_user(dn=dn)
        logger.debug("changed password for '%s'" % dn)
        return 'result' in self.con.result and self.con.result['result'] == 0
