"""
Supervisr Core Account Methods to remove logic from views
"""

import logging

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from ..ldap_connector import LDAPConnector
from ..mailer import Mailer
from ..models import AccountConfirmation, Event, Product, UserProfile

LOGGER = logging.getLogger(__name__)

def signup(email, name, password, ldap=None):
    """
    Creates a new Django/LDAP user from email, name and password.
    """
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
    acc_conf = AccountConfirmation.objects.create(user=new_d_user)
    # Run Product auto_add
    Product.do_auto_add(new_d_user)
    # Send confirmation mail
    Mailer.send_account_confirm(new_d_user.email, acc_conf)
    # Add event for user
    Event.objects.create(
        user=new_d_user,
        message=_("You Signed up"),
        current=False)
    return True

def change_password(email, password, ldap=None, reset=False):
    """
    Reset Password for a Django/LDAP user
    """
    # Change Django password
    user = User.objects.get(email=email)
    user.set_password(password)
    user.save()
    # Update ldap password if LDAP is enabled
    if LDAPConnector.enabled():
        if ldap is None:
            ldap = LDAPConnector()
        ldap.change_password(password, mail=email)
    # Add event
    Event.objects.create(
        user=user,
        message=_("You changed your Password (%(kind)s)" % {
            'kind': _("non-reset") if reset is False else _("reset")
            }),
        current=True)
    LOGGER.debug("Successfully updated password for %s", email)
    return True

def resend_confirmation(user):
    """
    Resend confirmation email after invalidating all existing links
    """
    # Invalidate all other links for this user
    old_acs = AccountConfirmation.objects.filter(
        user=user)
    for old_ac in old_acs:
        old_ac.confirmed = True
        old_ac.save()
    # Create a new Confirmation and send mail
    new_ac = AccountConfirmation.objects.create(user=user)
    return Mailer.send_account_confirm(user.email, new_ac)
