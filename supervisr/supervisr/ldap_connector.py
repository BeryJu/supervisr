from django.conf import settings
import ldap
import ldap.modlist
import logging
import time
logger = logging.getLogger(__name__)

CONF = settings.LDAP

class LDAPConnector(object):

    con = None

    def __init__(self):
        super(LDAPConnector, self).__init__()
        self.con = ldap.initialize('ldap://'+CONF['server'])
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        for key, value in CONF['OPTIONS'].iteritems():
            self.con.set_option(key, value)
        if ldap.OPT_X_TLS in CONF['OPTIONS'] \
            and CONF['OPTIONS'][ldap.OPT_X_TLS] is True:
            self.con.start_tls_s()

    # Switch so we can easily disable LDAP
    @staticmethod
    def enabled():
        return True

    @staticmethod
    def _encode_pass(password):
        unicode_pass = unicode('\"' + str(password) + '\"', 'iso-8859-1')
        return  unicode_pass.encode('utf-16-le')

    def lookup_user(self, mail):
        # Find out dn for user
        filter = "(mail=%s)" % mail
        results = self.con.search_s(CONF['BASE_DN'], ldap.SCOPE_SUBTREE, filter, ['dn'])
        assert len(results) == 1
        assert len(results[0]) == 1
        return results[0][0]

    def bind(self):
        full_user = CONF['BIND_USER']+'@'+CONF['DOMAIN']
        try:
            self.con.bind_s(full_user, CONF['BIND_PASS'], ldap.AUTH_SIMPLE)
        except ldap.LDAPError as e:
            logger.error(e)

    def auth_user(self, mail, password, rebind=False):
        dn = self.lookup_user(mail)
        # Try to bind as new user
        try:
            self.con.bind_s(results[0][0], password, ldap.AUTH_SIMPLE)
            return True
        except ldap.INVALID_CREDENTIALS as e:
            logger.debug("User %s failed to login (Wrong credentials)" % mail)
        except Exception as e:
            logger.error(e)
        # Optionally rebind
        # useful is same instance of this clss is used multiple times
        if rebind is True:
            self.con.unbind_s()
            self.bind()
        return False

    def check_email_used(self, mail):
        filter = "(mail=%s)" % mail
        results = self.con.search_s(CONF['BASE_DN'], ldap.SCOPE_SUBTREE, filter, ['dn'])
        return len(results) == 1

    def create_user(self, user, raw_password):
        # Sanity check first
        assert user.username == user.email
        # The dn of our new entry/object
        username = user.id + '_' + user.first_name + '_' + user.last_name
        cn = 'cn='+username
        dn = cn + ','+ CONF['CREATE_BASE']
        logger.debug('New CN: '+cn)
        logger.debug('New DN: '+dn)
        attrs = {
            'cn'               : cn,
            'description'      : time.time(),
            'sAMAccountName'   : username,
            'givenName'        : user.first_name,
            'sn'               : user.last_name,
            'displayName'      : user.id + ' - ' + user.first_name + ' ' + user.last_name,
            'mail'             : user.email,
            'userPrincipalName': username+'@'+CONF['DOMAIN'],
        }
        ldif = ldap.modlist.addModlist(attrs)
        return self.con.add_s(dn,ldif)

    def change_password(self, mail, old_password, new_password):
        dn = self.lookup_user(mail)
        # Reset Password
        mod = [
            (ldap.MOD_DELETE, 'unicodePwd', [LDAP._encode_pass(old_password)])
            (ldap.MOD_ADD, 'unicodePwd', [LDAP._encode_pass(new_password)])
        ]
        l.modify_s(dn, mod)
        l.unbind_s()
