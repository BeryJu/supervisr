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
    ac = AccountConfirmation.objects.create(user=new_d_user)
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

def change_password(email, password, ldap=None, reset=False):
    # Change Django password
    u = User.objects.get(email=email)
    u.set_password(password)
    u.save()
    # Update ldap password if LDAP is enabled
    if LDAPConnector.enabled():
        if ldap is None:
            ldap = LDAPConnector()
        ldap.change_password(password, mail=email)
    # Add event
    Event.objects.create(
        user=u,
        message=_("You changed your Password (%(kind)s)" % {
            'kind': _("non-reset") if reset is False else _("reset")
            }),
        current=True)
    logger.debug("Successfully updated password for %s" % email)
    return True

def resend_confirmation(user):
    # Invalidate all other links for this user
    old_acs = AccountConfirmation.objects.filter(
        user=user)
    for old_ac in old_acs:
        old_ac.confirmed = True
        old_ac.save()
    # Create a new Confirmation and send mail
    new_ac = AccountConfirmation.objects.create(user=user)
    return Mailer.send_account_confirmation(user.email, new_ac)
