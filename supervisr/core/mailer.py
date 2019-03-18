"""Supervisr Core Mail helper"""

import logging
from smtplib import SMTPException
from typing import List

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import loader
from htmlmin.minify import html_minify

from supervisr.core.celery import CELERY_APP
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
        raise ValueError("Either text or template must be supplied.")

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
            # If debug is disabled, minify HTML to save bandwidth
            html = _template.render(context)
            if not settings.DEBUG:
                html = html_minify(html)
            email.attach_alternative(html, 'text/html')
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
        raise
