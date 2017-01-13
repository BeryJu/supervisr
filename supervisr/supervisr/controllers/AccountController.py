import logging

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ..forms.account import ChangePasswordForm, LoginForm, SignupForm
from ..ldap_connector import LDAPConnector
from ..mailer import Mailer
from ..models import *

logger = logging.getLogger(__name__)

def signup(email, name, password, ldap=None):
    # Create django user
    new_d_user = User.objects.create_user(
        username=email,
        email=email,
        first_name=name)
    new_d_user.save()
    new_d_user.is_active = False
    new_d_user.set_password(password)
    new_d_user.save()
    # Create user profile
    new_up = UserProfile(user=new_d_user)
    new_up.save()
    # Create LDAP user if LDAP is active
    if LDAPConnector.enabled():
        if ldap is None:
            ldap = LDAPConnector()
        # Returns false if user could not be created
        if not ldap.create_user(new_d_user, password):
            # Add message what happend and return
            new_d_user.delete()
            return False
        ldap.disable_user(new_d_user.email)
    # Send confirmation email
    ac = AccountConfirmation(user=new_d_user)
    ac.save()
    # Run Product auto_add
    Product.do_auto_add(new_d_user)
    # Send confirmation mail
    Mailer.send_account_confirmation(new_d_user.email, ac)
    # Add event for user
    Event.objects.create(
        user=new_d_user,
        message=_("You Signed up"),
        current=False)
    return True

def change_password(email, password, ldap=None):
    # Change Django password
    u = User.objects.get(email=email)
    u.set_password(password)
    u.save()
    # Update ldap password if LDAP is enabled
    if LDAPConnector.enabled():
        if ldap is None:
            ldap = LDAPConnector()
        ldap.change_password(password, mail=email)
    logger.debug("Successfully updated password for %s" % email)
    return True
