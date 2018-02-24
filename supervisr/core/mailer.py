"""
Supervisr Core Mail helper
"""

import logging
from socket import gaierror

from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django.template import loader
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from supervisr.core.models import AccountConfirmation, Setting
from supervisr.core.signals import (SIG_USER_PASS_RESET_INIT,
                                    SIG_USER_POST_SIGN_UP,
                                    SIG_USER_RESEND_CONFIRM)

LOGGER = logging.getLogger(__name__)


def send_message(recipients, subject, **kwargs):
    """
    Send emails with more options. Following keys are used from kwargs:
      - template: Path to the HTML to send
      - template_context: Context used to render said template.
      - from: Optional from address, defaults to settings.EMAIL_FROM
      - text: Optional plain text
    """
    django_kwargs = {}
    # Handle HTML Templates
    if 'template' in kwargs:
        template = loader.get_template(kwargs['template'])
        if 'template_context' in kwargs:
            ctx = kwargs['template_context']
        else:
            ctx = {}
        django_kwargs['html_message'] = template.render(ctx)
    # Handle custom 'From: ' Addresses
    if 'from' in kwargs:
        django_from = kwargs['from']
    else:
        django_from = settings.EMAIL_FROM
    # Handle Plaintext body
    if 'text' in kwargs:
        django_text = kwargs['text']
    else:
        django_text = ''

    try:
        # Actually send the mail
        sent = send_mail(subject, django_text, django_from, \
            recipients, **django_kwargs)
        LOGGER.debug("Sent '%s' email to %s: %s", subject, recipients, sent)
        return sent == 1 # send_mail returns either 0 or 1
    except (ConnectionRefusedError, gaierror) as exc:
        # Always return true when debugging
        if settings.DEBUG:
            LOGGER.warning("Failed to send email %s", str(exc))
            return True
        else:
            raise

@receiver(SIG_USER_POST_SIGN_UP)
# pylint: disable=unused-argument
def mail_handle_user_signed_up(sender, signal, user, request, **kwargs):
    """
    Send the user a confirmation email
    """
    acc_confs = AccountConfirmation.objects.filter(
        user=user,
        kind=AccountConfirmation.KIND_SIGN_UP)
    if acc_confs.first() is not None:
        acc_conf = acc_confs.first()
    else:
        return False
    # Make URL for confirmation email
    domain = Setting.get('domain')
    branding = Setting.get('branding')
    url = domain + reverse('account-confirm',
                           kwargs={'uuid': acc_conf.pk})
    return send_message(
        recipients=[user.email],
        subject=_("Confirm your account on %(branding)s" % {
            'branding': branding}),
        template='email/acount_confirm.html',
        template_context={'url': url})

@receiver(SIG_USER_RESEND_CONFIRM)
def mail_handle_user_resend_confirm(sender, signal, user, request, **kwargs):
    """
    Resend the user a confirmation email
    """
    return mail_handle_user_signed_up(sender, signal, user, request, **kwargs)

@receiver(SIG_USER_PASS_RESET_INIT)
# pylint: disable=unused-argument
def mail_handle_pass_reset_init(sender, signal, user, **kwargs):
    """
    Send Email when password is to be reset
    """
    acc_confs = AccountConfirmation.objects.filter(
        user=user,
        kind=AccountConfirmation.KIND_PASSWORD_RESET)
    if acc_confs.first() is not None:
        acc_conf = acc_confs.first()
    else:
        return False
    # Make URL for confirmation email
    domain = Setting.get('domain')
    branding = Setting.get('branding')
    url = domain + reverse('account-reset_password_confirm',
                           kwargs={'uuid': acc_conf.pk})
    return send_message(
        recipients=[user.email],
        subject=_("Step 2/3 - Reset your Password on %(branding)s" % {
            'branding': branding}),
        template='email/acount_password_reset.html',
        template_context={'url': url})
