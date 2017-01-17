"""
Supervisr Core Events
"""

from django.dispatch import receiver
from django.utils.translation import ugettext as _

from .models import Event
from .signals import (SIG_USER_CHANGED_PASS,
                      SIG_USER_PRODUCT_RELATIONSHIP_CREATED,
                      SIG_USER_PRODUCT_RELATIONSHIP_DELETED,
                      SIG_USER_SIGNED_UP)


@receiver(SIG_USER_SIGNED_UP)
# pylint: disable=unused-argument
def event_handle_user_signed_up(sender, signal, user, **kwargs):
    """
    Create an Event when a user signed up
    """
    Event.objects.create(
        user=user,
        message=_("You Signed up"),
        current=False)

@receiver(SIG_USER_CHANGED_PASS)
# pylint: disable=unused-argument
def event_handle_user_changed_pass(signal, user, was_reset, **kwargs):
    """
    Create an Event when a user changes their password
    """
    Event.objects.create(
        user=user,
        message=_("You changed your Password (%(kind)s)" % {
            'kind': _("non-reset") if was_reset is False else _("reset")
            }),
        current=True)

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
def event_handle_upr_deleted(sender, signal, upr):
    """
    Create an Event to let users know that they lost access to a Product
    """
    Event.objects.create(
        user=upr.user,
        message=_("You lost access to %(product)s" % {
            'product': upr.product
            }),
        current=True)
