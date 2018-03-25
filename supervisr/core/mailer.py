"""Supervisr Core Mail helper"""

import logging
from smtplib import SMTPException
from typing import List

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.dispatch import receiver
from django.template import loader
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from supervisr.core.celery import CELERY_APP
from supervisr.core.models import AccountConfirmation, Setting, User
from supervisr.core.signals import (SIG_USER_PASS_RESET_INIT,
                                    SIG_USER_POST_SIGN_UP,
                                    SIG_USER_RESEND_CONFIRM)
from supervisr.core.tasks import SupervisrTask

LOGGER = logging.getLogger(__name__)


@CELERY_APP.task(bind=True, base=SupervisrTask)
# pylint: disable=too-many-arguments, too-many-locals
def send_message(
        self, recipients: List[str], subject: str, template: str = None,
        template_context: dict = None, from_address: str = None, text: str = None, **kwargs):
    """Send emails in the background. For each recipient a new E-Mail is generated.

    Args:
        recipients: List of E-Mail addresses we send to.
        subject: Subject of E-Mail.
        template: Optional path to a django template.
            This template is rendered and attached as text/html multipart
        template_context: Optional conext for template above.
        from_address: Optional Address we send E-Mail addresses from.
            If not given, we use the default from Settings
        text: Optional plaintext for the body
    """
    self.prepare(**kwargs)
    emails = []

    # If we don't have text and template, return now.
    if not text and not template:
        return False

    for recipient in recipients:
        # Create a separate email for each recipient
        email = EmailMultiAlternatives()
        email.from_email = from_address if from_address else settings.EMAIL_FROM
        email.body = text if text else ''
        email.to = [recipient]
        email.subject = subject
        if template:
            _template = loader.get_template(template)
            context = template_context if template_context else {}
            # Lookup user from recipient address, to give it to the template
            users = User.objects.filter(email=recipient)
            if users.exists():
                context['_user'] = users.first()
            email.attach_alternative(_template.render(context), 'text/html')
        LOGGER.debug("Prepared E-Mail '%s' to %s", subject, recipient)
        emails.append(email)

    try:
        with get_connection() as connection:
            sent = connection.send_messages(emails)
        return sent == len(emails)  # send_messages returns amount of emails sent
    except SMTPException as exc:
        # Always return true when debugging
        if settings.DEBUG:
            LOGGER.warning("Failed to send emails %r", exc)
            return True
        else:
            raise


@receiver(SIG_USER_POST_SIGN_UP)
# pylint: disable=unused-argument
def mail_handle_user_signed_up(sender, signal, user, request, **kwargs):
    """Send the user a confirmation email"""
    account_confirmations = AccountConfirmation.objects.filter(
        user=user,
        kind=AccountConfirmation.KIND_SIGN_UP)
    if account_confirmations.first() is not None:
        account_confirmation = account_confirmations.first()
    else:
        return False
    # Make URL for confirmation email
    domain = Setting.get('domain')
    branding = Setting.get('branding')
    url = domain + reverse('account-confirm', kwargs={'uuid': account_confirmation.pk})
    return send_message.delay(
        recipients=[user.email],
        subject=_("Confirm your account on %(branding)s" %
                  {
                      'branding': branding
                  }),
        template='email/account_confirm.html',
        template_context={'url': url}
    )


@receiver(SIG_USER_RESEND_CONFIRM)
def mail_handle_user_resend_confirm(sender, signal, user, request, **kwargs):
    """Resend the user a confirmation email"""
    return mail_handle_user_signed_up(sender, signal, user, request, **kwargs)


@receiver(SIG_USER_PASS_RESET_INIT)
# pylint: disable=unused-argument
def mail_handle_pass_reset_init(sender, signal, user, **kwargs):
    """Send Email when password is to be reset"""
    account_confirmations = AccountConfirmation.objects.filter(
        user=user,
        kind=AccountConfirmation.KIND_PASSWORD_RESET)
    if account_confirmations.first() is not None:
        account_confirmations = account_confirmations.first()
    else:
        return False
    # Make URL for confirmation email
    domain = Setting.get('domain')
    branding = Setting.get('branding')
    url = domain + reverse('account-reset_password_confirm',
                           kwargs={'uuid': account_confirmations.pk})
    return send_message.delay(
        recipients=[user.email],
        subject=_("Step 2/3 - Reset your Password on %(branding)s" %
                  {
                      'branding': branding
                  }),
        template='email/account_password_reset.html',
        template_context={'url': url}
    )
