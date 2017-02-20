"""
Supervisr mod_ldap Signals
"""

from django.dispatch import receiver
from ldap3 import version as ldap3_version

from supervisr.signals import (SIG_CHECK_USER_EXISTS, SIG_GET_MOD_INFO,
                               SIG_USER_CHANGE_PASS, SIG_USER_CONFIRM,
                               SIG_USER_PRODUCT_RELATIONSHIP_CREATED,
                               SIG_USER_PRODUCT_RELATIONSHIP_DELETED,
                               SIG_USER_SIGN_UP)

from .ldap_connector import LDAPConnector


@receiver(SIG_USER_SIGN_UP)
# pylint: disable=unused-argument
def ldap_handle_user_sign_up(sender, signal, user, password, **kwargs):
    """
    Create LDAP user if LDAP is active
    """
    if LDAPConnector.enabled():
        ldap = LDAPConnector()
        # Returns false if user could not be created
        if not ldap.create_user(user, password):
            # Add message what happend and return
            user.delete()
            return False
        ldap.disable_user(user.email)

@receiver(SIG_USER_CHANGE_PASS)
# pylint: disable=unused-argument
def ldap_handle_change_pass(sender, signal, user, password, **kwargs):
    """
    Update ldap password if LDAP is enabled
    """
    if LDAPConnector.enabled():
        ldap = LDAPConnector()
        ldap.change_password(password, mail=user.email)

@receiver(SIG_USER_CONFIRM)
#pylint: disable=unused-argument
def ldap_handle_user_confirm(sender, signal, user, **kwargs):
    """
    activate LDAP user
    """
    if LDAPConnector.enabled():
        ldap = LDAPConnector()
        ldap.enable_user(user.email)

@receiver(SIG_USER_PRODUCT_RELATIONSHIP_CREATED)
# pylint: disable=unused-argument
def ldap_handle_upr_created(sender, signal, upr, **kwargs):
    """
    Handle creation of user_product_relationship, add to ldap group if needed
    """
    if LDAPConnector.enabled() and upr.product.ldap_group:
        ldap = LDAPConnector()
        ldap.add_to_group(
            group_dn=upr.product.ldap_group,
            mail=upr.user.email)

@receiver(SIG_USER_PRODUCT_RELATIONSHIP_DELETED)
# pylint: disable=unused-argument
def ldap_handle_upr_deleted(sender, signal, upr, **kwargs):
    """
    Handle deletion of user_product_relationship, remove from group if needed
    """
    if LDAPConnector.enabled() and upr.product.ldap_group:
        ldap = LDAPConnector()
        ldap.remove_from_group(
            group_dn=upr.product.ldap_group,
            mail=upr.user.email)

@receiver(SIG_CHECK_USER_EXISTS)
# pylint: disable=unused-argument
def ldap_handle_check_user(sender, signal, email, **kwargs):
    """
    Check if user exists in LDAP
    """
    if LDAPConnector.enabled():
        ldap = LDAPConnector()
        if ldap.is_email_used(email):
            return True
    return False

@receiver(SIG_GET_MOD_INFO)
# pylint: disable=unused-argument
def ldap_handle_get_mod_info(sender, signal, **kwargs):
    """
    Return some infos about this module
    """
    return {
        'LDAP3 Version': ldap3_version.__version__,
        'LDAP Enabled': LDAPConnector.enabled,
        'LDAP Server': LDAPConnector.get_server,
    }
