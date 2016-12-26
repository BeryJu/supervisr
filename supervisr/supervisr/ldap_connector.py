from django.conf import settings
from ldap3 import Server, Connection, ALL
from ldap3 import MODIFY_REPLACE
from ldap3.core.exceptions import LDAPInvalidCredentialsResult
from ldap3.extend.microsoft.modifyPassword import modify_ad_password
from ldap3.extend.microsoft.unlockAccount import unlock_ad_account
import logging
import time
logger = logging.getLogger(__name__)

CONF = settings.LDAP
ENABLED = settings.LDAP_ENABLED

class LDAPConnector(object):

    con = None

    def __init__(self):
        super(LDAPConnector, self).__init__()
        self.server = Server(CONF['SERVER'])
        full_user = CONF['BIND_USER']+'@'+CONF['DOMAIN']
        self.con = Connection(self.server, raise_exceptions=True,
            user=full_user, password=CONF['BIND_PASS'])
        self.con.bind()
        self.con.start_tls()

    # Switch so we can easily disable LDAP
    @staticmethod
    def enabled():
        return ENABLED

    @staticmethod
    def encode_pass(password):
        return '"{}"'.format(password).encode('utf-16-le')

    def lookup_user(self, mail, field='distinguishedName'):
        # Find out dn for user
        filter = "(mail=%s)" % mail
        assert self.con.search(CONF['BASE'], filter, attributes=[field]) == True
        results = self.con.entries
        assert len(results) == 1
        return results[0][field].raw_values[0]

    def auth_user(self, mail, password):
        upn = self.lookup_user(mail, field='userPrincipalName')
        # Try to bind as new user
        logger.debug("binding as %s" % upn)
        try:
            t_con = Connection(self.server, user=upn, password=password, raise_exceptions=True)
            t_con.bind()
            return True
        except LDAPInvalidCredentialsResult as e:
            logger.debug("User %s failed to login (Wrong credentials)" % upn)
        except Exception as e:
            logger.error(e)
        return False

    def is_email_used(self, mail):
        filter = "(mail=%s)" % mail
        self.con.search(CONF['BASE'], filter, attributes=['mail'])
        return len(self.con.entries) == 1

    def create_user(self, user, raw_password):
        # The dn of our new entry/object
        username = 'c_' + str(user.id) + '_' + user.username
        dn = 'cn='+username+','+CONF['CREATE_BASE']
        logger.info('New DN: '+dn)
        attrs = {
            'cn'                : str(username),
            'description'       : str('t='+str(time.time())),
            'sAMAccountName'    : str(username),
            'givenName'         : str(user.username),
            'displayName'       : str(username),
            'mail'              : str(user.email),
            'userPrincipalName' : str(username+'@'+CONF['DOMAIN']),
            'objectclass'       : ['top','person','organizationalPerson', 'user'],
        }
        self.con.add(dn, 'user', attrs)
        return self.change_password(user.email, raw_password)

    def disable_account(self, mail):
        dn = self.lookup_user(mail)
        self.con.modify(dn, {
            'userAccountControl': [(MODIFY_REPLACE, [str(66050)])],
        })
        logger.debug("disabled account %s" % mail)
        return self.con.result

    def enable_account(self, mail):
        dn = self.lookup_user(mail)
        self.con.modify(dn, {
            'userAccountControl': [(MODIFY_REPLACE, [str(66048)])],
        })
        logger.debug("disabled account %s" % mail)
        return self.con.result

    def change_password(self, mail, new_password):
        dn = self.lookup_user(mail)
        self.con.modify(dn, {
            'unicodePwd': [(MODIFY_REPLACE, [LDAPConnector.encode_pass(new_password)])],
        })
        self.con.modify(dn, {
            'userAccountControl': [(MODIFY_REPLACE, [str(66048)])],
        })
        logger.debug("changed password for %s" % mail)
        return self.con.result
