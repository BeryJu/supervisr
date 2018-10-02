"""Supervisr mod_ldap Signals"""

from django.conf import settings
from django.dispatch import receiver
from ldap3 import version as ldap3_version
from ldap3.core.exceptions import LDAPCommunicationError, LDAPException

from supervisr.core.models import Product
from supervisr.core.signals import (get_module_health, get_module_info,
                                    on_check_user_exists,
                                    on_user_acquirable_relationship_created,
                                    on_user_acquirable_relationship_deleted,
                                    on_user_change_password, on_user_confirmed,
                                    on_user_sign_up)
from supervisr.mod.auth.ldap.ldap_connector import LDAPConnector

LDAP = None
if LDAPConnector.enabled():
    LDAP = LDAPConnector()


@receiver(on_user_sign_up)
# pylint: disable=unused-argument
def ldap_handle_user_sign_up(sender, signal, user, password, **kwargs):
    """Create LDAP user if LDAP is active"""
    if LDAP and LDAP.create_users_enabled:
        # Returns false if user could not be created
        if not LDAP.create_ldap_user(user, password):
            # Add message what happend and return
            user.delete()
            return False
        LDAP.disable_user(mail=user.email)
        return True
    return None


@receiver(on_user_change_password)
# pylint: disable=unused-argument
def ldap_handle_change_pass(sender, signal, user, password, **kwargs):
    """Update ldap password if LDAP is enabled"""
    if LDAP and LDAP.create_users_enabled:
        LDAP.change_password(password, mail=user.email)


@receiver(on_user_confirmed)
# pylint: disable=unused-argument
def ldap_handle_user_confirm(sender, signal, user, **kwargs):
    """activate LDAP user"""
    if LDAP and LDAP.create_users_enabled:
        LDAP.enable_user(mail=user.email)


@receiver(on_user_acquirable_relationship_created)
# pylint: disable=unused-argument
def ldap_handle_relationship_created(sender, signal, relationship, **kwargs):
    """Handle creation of user_product_relationship, add to ldap group if needed"""
    if LDAP and LDAP.create_users_enabled and isinstance(relationship.model, Product):
        exts = relationship.model.extensions.filter(productextensionldap__isnull=False)
        if exts.exists():
            LDAP.add_to_group(
                group_dn=exts.first().ldap_group,
                mail=relationship.user.email)


@receiver(on_user_acquirable_relationship_deleted)
# pylint: disable=unused-argument
def ldap_handle_relationship_deleted(sender, signal, relationship, **kwargs):
    """Handle deletion of user_product_relationship, remove from group if needed"""
    if LDAP and LDAP.create_users_enabled and isinstance(relationship.model, Product):
        exts = relationship.model.extensions.filter(productextensionldap__isnull=False)
        if exts.exists():
            LDAP.remove_from_group(
                group_dn=exts.first().ldap_group,
                mail=relationship.user.email)


@receiver(on_check_user_exists)
# pylint: disable=unused-argument
def ldap_handle_check_user(sender, signal, email, **kwargs):
    """Check if user exists in LDAP"""
    if LDAP and LDAP.create_users_enabled:
        try:
            if LDAP.is_email_used(email) and not settings.TEST:
                return True
        except LDAPCommunicationError:
            return False
    return False


@receiver(get_module_info)
# pylint: disable=unused-argument
def ldap_handle_get_mod_info(sender, signal, **kwargs):
    """Return some infos about this module"""
    return {
        'LDAP3 Version': ldap3_version.__version__,
        'LDAP Enabled': LDAPConnector.enabled(),
        'LDAP Server': LDAPConnector.get_server(),
    }


@receiver(get_module_health)
# pylint: disable=unused-argument
def ldap_handle_get_mod_health(sender, signal, **kwargs):
    """Return LDAP health"""
    try:
        if LDAPConnector.enabled():
            LDAPConnector()
        return True
    except LDAPException:
        return False
