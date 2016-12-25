from django.conf import settings
import ldap
import ldap.modlist
import logging
import time
logger = logging.getLogger(__name__)

CONF = settings.LDAP
ENABLED = settings.LDAP_ENABLED

class LDAPConnector(object):

    con = None
    is_bound = False

    def __init__(self):
        super(LDAPConnector, self).__init__()
        self.con = ldap.initialize('ldaps://'+CONF['SERVER'])
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        for key, value in CONF['OPTIONS'].iteritems():
            self.con.set_option(key, value)
#        if ldap.OPT_X_TLS in CONF['OPTIONS'] \
#            and CONF['OPTIONS'][ldap.OPT_X_TLS] is True:
#            self.con.start_tls_s()

    # Switch so we can easily disable LDAP
    @staticmethod
    def enabled():
        return ENABLED

    @staticmethod
    def encode_pass(password):
        unicode_pass = unicode('\"' + str(password) + '\"')
        return unicode_pass.encode('utf-16-le')

    def lookup_user(self, mail):
        assert self.is_bound == True
        # Find out dn for user
        filter = "(mail=%s)" % mail
        results = self.con.search_s(CONF['BASE'], ldap.SCOPE_SUBTREE, filter, ['distinguishedName'])
        assert len(results) == 1
        assert len(results[0]) >= 1
        return results[0][0]

    def bind(self):
        full_user = CONF['BIND_USER']+'@'+CONF['DOMAIN']
        try:
            self.con.bind_s(full_user, CONF['BIND_PASS']) #, ldap.AUTH_SIMPLE)
            self.is_bound = True
        except ldap.LDAPError as e:
            logger.error(e)
            self.is_bound = False

    def auth_user(self, mail, password, rebind=False):
        assert self.is_bound == True
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
        assert self.is_bound == True
        filter = "(mail=%s)" % mail
        results = self.con.search_s(CONF['BASE'], ldap.SCOPE_SUBTREE, filter, ['dn'])
        return len(results) == 1

    def create_user(self, user, raw_password):
        # Sanity check first
        assert self.is_bound == True
        # The dn of our new entry/object
        username = 'c_' + str(user.id) + '_' + user.username
        dn = 'cn='+username+','+CONF['CREATE_BASE']
        logger.info('New DN: '+dn)
        attrs = {
            'cn'               : str(username),
            'description'      : str('t='+str(time.time())),
            'sAMAccountName'   : str(username),
            'givenName'        : str(user.username),
            'displayName'      : str(username),
            'mail'             : str(user.email),
            'userPrincipalName': str(username+'@'+CONF['DOMAIN']),
            'objectclass'      : ['top','person','organizationalPerson', 'user'],
        }
        ldif = ldap.modlist.addModlist(attrs)
        add = self.con.add_s(dn, ldif)
        return self.change_password(user.email, None, raw_password)

    def change_password(self, mail, old_password, new_password):
        assert self.is_bound == True
        dn = self.lookup_user(mail)
        # Reset Password
        mods = []
        if old_password is not None:
            mods.append((ldap.MOD_DELETE, 'unicodePwd', [LDAPConnector.encode_pass(old_password)]))
        mods.append((ldap.MOD_ADD, 'unicodePwd', [LDAPConnector.encode_pass(new_password)]))
        return self.con.modify_s(dn, mods)
