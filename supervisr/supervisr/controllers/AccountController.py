"""
Supervisr Core Account Methods to remove logic from views
"""

import logging

from django.contrib.auth.models import User

from ..ldap_connector import LDAPConnector
from ..mailer import Mailer
from ..models import AccountConfirmation, Product, UserProfile
from ..signals import SIG_USER_CHANGED_PASS, SIG_USER_SIGNED_UP

LOGGER = logging.getLogger(__name__)

def signup(email, name, password, ldap=None):
    """
    Creates a new Django/LDAP user from email, name and password.
    """
    # Create django user
    new_user = User.objects.create_user(
        username=email,
        email=email,
        first_name=name)
    new_user.save()
    new_user.is_active = False
    new_user.set_password(password)
    new_user.save()
    # Create user profile
    new_up = UserProfile(user=new_user)
    new_up.save()
    # Create LDAP user if LDAP is active
    if LDAPConnector.enabled():
        if ldap is None:
            ldap = LDAPConnector()
        # Returns false if user could not be created
        if not ldap.create_user(new_user, password):
            # Add message what happend and return
            new_user.delete()
            return False
        ldap.disable_user(new_user.email)
    # Send confirmation email
    acc_conf = AccountConfirmation.objects.create(user=new_user)
    # Run Product auto_add
    Product.do_auto_add(new_user)
    # Send confirmation mail
    Mailer.send_account_confirm(new_user.email, acc_conf)
    # Send event for user creation
    SIG_USER_SIGNED_UP.send(
        sender=None,
        user=new_user)
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
    # Trigger Event
    SIG_USER_CHANGED_PASS.send(
        sender=None,
        user=user,
        was_reset=reset)
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
