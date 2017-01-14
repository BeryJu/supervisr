"""
Supervisr Core Mail helper
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, loader
from django.urls import reverse
from django.utils.translation import ugettext as _

from .models import Setting


class Mailer(object):
    """
    Utility functions to easier send mails with templates
    """

    @staticmethod
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
                ctx = Context(kwargs['template_context'])
            else:
                ctx = Context()
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

        # Actually send the mail
        sent = send_mail(subject, django_text, django_from, \
            recipients, **django_kwargs)
        return sent == 1 # send_mail returns either 0 or 1

    @staticmethod
    def send_account_confirm(recipient, confirmation):
        """
        Wrapper for send_message to send account confirmation email
        """
        # Make URL for confirmation email
        domain = Setting.get('supervisr:domain')
        branding = Setting.get('supervisr:branding')
        url = domain + reverse('account-confirm',
                               kwargs={'uuid': confirmation.pk})
        return Mailer.send_message(
            recipients=[recipient],
            subject=_("Confirm your account on %(branding)s" % {
                'branding': branding}),
            template='email/acount_confirm.html',
            template_context={'url': url})

    @staticmethod
    def send_password_reset_confirm(recipient, confirmation):
        """
        Wrapper for send_message to send password reset email
        """
        # Make URL for confirmation email
        domain = Setting.get('supervisr:domain')
        branding = Setting.get('supervisr:branding')
        url = domain + reverse('account-reset_password_confirm',
                               kwargs={'uuid': confirmation.pk})
        return Mailer.send_message(
            recipients=[recipient],
            subject=_("Step 2/3 - Reset your Password on %(branding)s" % {
                'branding': branding}),
            template='email/acount_password_reset.html',
            template_context={'url': url})
