"""
Supervisr Core Account Methods to remove logic from views
"""

import logging

from django.contrib.auth.models import User

from ..models import AccountConfirmation, Product, UserProfile
from ..signals import (SIG_USER_CHANGE_PASS, SIG_USER_POST_CHANGE_PASS,
                       SIG_USER_POST_SIGN_UP, SIG_USER_RESEND_CONFIRM,
                       SIG_USER_SIGN_UP)

LOGGER = logging.getLogger(__name__)

def signup(email, name, password, request=None):
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
    # Send signal for other auth sources
    SIG_USER_SIGN_UP.send(
        sender=None,
        user=new_user,
        req=request,
        password=password)
    # Create Account Confirmation UUID
    AccountConfirmation.objects.create(user=new_user)
    # Run Product auto_add
    Product.do_auto_add(new_user)
    # Send event for user creation
    SIG_USER_POST_SIGN_UP.send(
        sender=None,
        user=new_user,
        req=request)
    return True

def change_password(email, password, reset=False, request=None):
    """
    Reset Password for a Django/LDAP user
    """
    # Change Django password
    user = User.objects.get(email=email)
    user.set_password(password)
    user.save()
    # Send signal for other auth sources
    SIG_USER_CHANGE_PASS.send(
        sender=None,
        user=user,
        req=request,
        password=password)
    # Trigger Event
    SIG_USER_POST_CHANGE_PASS.send(
        sender=None,
        user=user,
        was_reset=reset,
        req=request)
    LOGGER.debug("Successfully updated password for %s", email)
    return True

def resend_confirmation(user, request=None):
    """
    Resend confirmation email after invalidating all existing links
    """
    # Invalidate all other links for this user
    old_acs = AccountConfirmation.objects.filter(
        user=user)
    for old_ac in old_acs:
        old_ac.confirmed = True
        old_ac.save()
    # Create Account Confirmation UUID
    AccountConfirmation.objects.create(user=user)
    SIG_USER_RESEND_CONFIRM.send(
        sender=None,
        user=user,
        req=request)
    return True
