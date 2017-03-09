"""
Supervisr Core Events
"""

from django.dispatch import receiver
from django.utils.translation import ugettext as _

from .models import Event
from .signals import (SIG_USER_LOGIN, SIG_USER_LOGOUT,
                      SIG_USER_POST_CHANGE_PASS, SIG_USER_POST_SIGN_UP,
                      SIG_USER_PRODUCT_RELATIONSHIP_CREATED,
                      SIG_USER_PRODUCT_RELATIONSHIP_DELETED)
from .utils import get_remote_ip, get_reverse_dns


@receiver(SIG_USER_POST_SIGN_UP)
# pylint: disable=unused-argument
def event_handle_user_signed_up(sender, signal, user, req, **kwargs):
    """
    Create an Event when a user signed up
    """
    remote_ip = get_remote_ip(req)
    rdns = get_reverse_dns(remote_ip)
    Event.objects.create(
        user=user,
        message=_("You Signed up"),
        current=False,
        remote_ip=remote_ip,
        remote_ip_rdns=rdns)

@receiver(SIG_USER_POST_CHANGE_PASS)
# pylint: disable=unused-argument
def event_handle_user_changed_pass(signal, user, req, was_reset, **kwargs):
    """
    Create an Event when a user changes their password
    """
    remote_ip = get_remote_ip(req)
    rdns = get_reverse_dns(remote_ip)
    Event.objects.create(
        user=user,
        message=_("You changed your Password (%(kind)s)" % {
            'kind': _("non-reset") if was_reset is False else _("reset")
            }),
        current=True,
        remote_ip=remote_ip,
        remote_ip_rdns=rdns)

@receiver(SIG_USER_PRODUCT_RELATIONSHIP_CREATED)
# pylint: disable=unused-argument
def event_handle_upr_created(sender, signal, upr, **kwargs):
    """
    Create an Event when a UserProductRelationship was created
    """
    Event.objects.create(
        user=upr.user,
        message=_("You gained access to %(product)s" % {
            'product': upr.product
            }),
        current=True)

@receiver(SIG_USER_PRODUCT_RELATIONSHIP_DELETED)
# pylint: disable=unused-argument
def event_handle_upr_deleted(sender, signal, upr, **kwargs):
    """
    Create an Event to let users know that they lost access to a Product
    """
    Event.objects.create(
        user=upr.user,
        message=_("You lost access to %(product)s" % {
            'product': upr.product
            }),
        current=True)

@receiver(SIG_USER_LOGIN)
# pylint: disable=unused-argument
def event_handler_user_login(sender, signal, user, req, **kwargs):
    """
    Create a hidden event when a user logs in
    """
    remote_ip = get_remote_ip(req)
    rdns = get_reverse_dns(remote_ip)
    Event.objects.create(
        user=user,
        message=_("You logged in"),
        remote_ip=remote_ip,
        remote_ip_rdns=rdns,
        hidden=True,
        current=False)

@receiver(SIG_USER_LOGOUT)
# pylint: disable=unused-argument
def event_handler_user_logout(sender, signal, user, req, **kwargs):
    """
    Create a hidden event when a user logs out
    """
    remote_ip = get_remote_ip(req)
    rdns = get_reverse_dns(remote_ip)
    Event.objects.create(
        user=user,
        message=_("You logged in"),
        remote_ip=remote_ip,
        remote_ip_rdns=rdns,
        hidden=True,
        current=False)
