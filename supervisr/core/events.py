"""
Supervisr Core Events
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from .mailer import send_message
from .models import Event
from .signals import (SIG_USER_LOGIN, SIG_USER_LOGOUT,
                      SIG_USER_POST_CHANGE_PASS, SIG_USER_POST_SIGN_UP,
                      SIG_USER_PRODUCT_RELATIONSHIP_CREATED,
                      SIG_USER_PRODUCT_RELATIONSHIP_DELETED)


@receiver(SIG_USER_POST_SIGN_UP)
# pylint: disable=unused-argument
def event_handle_user_signed_up(sender, signal, user, req, **kwargs):
    """
    Create an Event when a user signed up
    """
    Event.create(
        user=user,
        message=_("You Signed up"),
        current=False,
        request=req)

@receiver(SIG_USER_POST_CHANGE_PASS)
# pylint: disable=unused-argument
def event_handle_user_changed_pass(signal, user, req, was_reset, **kwargs):
    """
    Create an Event when a user changes their password
    """
    Event.create(
        user=user,
        message=_("You changed your Password (%(kind)s)" % {
            'kind': _("non-reset") if was_reset is False else _("reset")
            }),
        current=True,
        request=req)

@receiver(SIG_USER_PRODUCT_RELATIONSHIP_CREATED)
# pylint: disable=unused-argument
def event_handle_upr_created(sender, signal, upr, **kwargs):
    """
    Create an Event when a UserProductRelationship was created
    """
    Event.create(
        user=upr.user,
        message=_("You gained access to %(name)s" % {
            'name': upr.name,
            }),
        current=True)

@receiver(SIG_USER_PRODUCT_RELATIONSHIP_DELETED)
# pylint: disable=unused-argument
def event_handle_upr_deleted(sender, signal, upr, **kwargs):
    """
    Create an Event to let users know that they lost access to a Product
    """
    Event.create(
        user=upr.user,
        message=_("You lost access to %(name)s" % {
            'name': upr.name,
            }),
        current=True)

@receiver(SIG_USER_LOGIN)
# pylint: disable=unused-argument
def event_handler_user_login(sender, signal, user, req, **kwargs):
    """
    Create a hidden event when a user logs in
    """
    Event.create(
        user=user,
        message=_("You logged in"),
        request=req,
        hidden=True,
        current=False)

@receiver(SIG_USER_LOGOUT)
# pylint: disable=unused-argument
def event_handler_user_logout(sender, signal, user, req, **kwargs):
    """
    Create a hidden event when a user logs out
    """
    Event.create(
        user=user,
        message=_("You logged in"),
        request=req,
        hidden=True,
        current=False)

@receiver(post_save, sender=Event)
# pylint: disable=unused-argument
def event_handler_send_mail(sender, signal, instance, **kwargs):
    """
    Send an email if an event with send_notification is created
    """
    if instance.send_notification is True:
        send_message(
            recipients=[instance.user.email],
            subject=instance.message,
            template='email/generic_email.html',
            template_context={'message': instance.message})
